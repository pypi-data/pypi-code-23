import json
import re
import urllib

import tornado
import tornado.httpclient
from flasky import errors
from quark_utilities import json_helpers
from tornado.httpclient import AsyncHTTPClient
from tornado.platform.asyncio import to_asyncio_future


class components_base(object):

    QUARK_QUERY_LIMIT = 500
    BASE_API = None
    DELIVERY_API= None
    DOMAIN_ID = None

    def __init__(self, settings):
        self.BASE_API = settings.get("base_api")
        self.DOMAIN_ID = settings.get("domain_id")
        self.DELIVERY_API = settings.get("base_delivery_api")

        self.http_client = AsyncHTTPClient()

    def set_token(self, token):
        if token:
            self.token = "Bearer {0}".format(token)

    def _handle_error_if_exist(self, response):

        if response.code <= 400:
            return

        err_body = json.loads(response.body.decode('utf-8')) if response else {}

        raise errors.FError(
            err_code=err_body['error'].get('err_code', err_body['error'].get('code', None)),
            err_msg=err_body['error'].get('err_msg', err_body['error'].get('message', None)),
            context=err_body['error']['context']
        )

    async def _get(self, url, api=None):
        api_url = self.BASE_API
        if api == 'delivery':
            api_url = self.DELIVERY_API

        url = urllib.parse.quote(url, safe=':?&=/')

        request = tornado.httpclient.HTTPRequest(
            method='GET',
            url="{0}/domains/{1}{2}".format(api_url, self.DOMAIN_ID, url),
            headers={
                'Authorization': self.token,
                'Accept': 'application/json'
            },
            connect_timeout=30
        )
        response = await self.http_client.fetch(request)

        self._handle_error_if_exist(response)

        return json.loads(response.body.decode("utf-8"))

    async def _post(self, url, body, headers=None, api=None):
        api_url = self.BASE_API
        if api == 'delivery':
            api_url = self.DELIVERY_API

        _body = json.dumps(body, default=json_helpers.bson_to_json)

        url = urllib.parse.quote(url, safe=':?&=/')

        url = "{0}/domains/{1}{2}".format(api_url, self.DOMAIN_ID, url)

        if not headers:
            headers = {
                'Authorization': self.token,
                'Content-Type': 'application/json'
            }

        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url=str(url),
            headers=headers,
            body=_body,
        )

        response = await to_asyncio_future(self.http_client.fetch(
            request,
            raise_error=False
        ))

        self._handle_error_if_exist(response)

        return json.loads(response.body.decode('utf-8'))

    async def _post_extended(self, base_url, body, limit, skip=0, sort=None):
        resp = {"data": {"items": [], "count": 0}}

        """
        Below generates query limits list. For ex:
        limit = 1233 and QUARK_QUERY_LIMIT = 500
        limit_lists = [500, 500, 233]
        """
        limit_list = [self.QUARK_QUERY_LIMIT] * int(limit / self.QUARK_QUERY_LIMIT) + [limit % self.QUARK_QUERY_LIMIT]

        for _limit in limit_list:
            url = base_url + "?limit={}&skip={}".format(_limit, skip)
            if sort:
                url = url + "&sort={}".format(sort)
            response = await self._post(url, body)
            if "error" not in response:
                resp["data"]["items"] += response["data"]["items"]

        resp["data"]["count"] = len(resp["data"]["items"])
        return resp

    async def _put(self, url, data, version):
        url = urllib.parse.quote(url, safe=':?&=/')
        request = tornado.httpclient.HTTPRequest(
            method='PUT',
            url="{0}/domains/{1}{2}".format(self.BASE_API, self.DOMAIN_ID, url),
            headers={
                'Authorization': self.token,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'x-update-version': str(version)
            },
            body=json.dumps(data, default=json_helpers.bson_to_json)
        )

        response = await self.http_client.fetch(
            request,
            raise_error=False
        )

        self._handle_error_if_exist(response)

        return json.loads(response.body.decode('utf-8'))

    async def _delete(self, url, data={}):
        url = urllib.parse.quote(url, safe=':?&=/')
        request = tornado.httpclient.HTTPRequest(
            method='DELETE',
            url="{0}/domains/{1}{2}".format(self.BASE_API, self.DOMAIN_ID, url),
            headers={
                'Authorization': self.token,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body=json.dumps(data, default=json_helpers.bson_to_json),
            allow_nonstandard_methods=True
        )

        response = await self.http_client.fetch(
            request,
            raise_error=False
        )

        self._handle_error_if_exist(response)

    def prepare_query(self, params, ignore=[]):

        if not params.get('limit', None):
            params['limit'] = 500

        if not params.get('skip', None):
            params['skip'] = 0

        if not params.get('sort', None):
            params['sort'] = "sys.created_at desc"

        if not params.get('document', None):
            params['document'] = {}

        for key in ignore:
            try:
                del params[key]
            except Exception:
                pass

        return params

    def update_filters(self, document, params):
        if not document.get("where", None):
            document['where'] = {}

        for key, val in params.items():
            document['where'].update({key:val})

    def update_attributes(self, document, params):
        for key, val in params.items():
            document['where'].update({key:val})

    async def expand_content_field(self, content):
        playlist_expand_list = {
            'data': {
                'items': []
            }
        }

        if not content.get('relations'):
            content['relations'] = {}

        if content['type'] == 'playlist' and content.get('playlist_items'):

                playlist_items = await self._post('/contents/_query', {
                    'where': {'_id': {'$in': content['playlist_items']}},
                    'select': {'title': 1, 'images': 1, 'description': 1}
                })
                playlist_expand_list = playlist_items
        content['relations']['playlist_items'] = playlist_expand_list['data']['items']

    def prepare_endpoint(self, module, method, limit=None, skip=None, sort=None ):
        url = '/' + module +'/' + method + \
              '?limit={}&skip={}&sort={}'.format(limit, skip, sort)
        return url

    def prepare_delivery_endpoint(self, module, **kwargs ):
        query_string = []
        keys = ['method', 'limit', 'skip', 'select', 'types', 'paths', 'q', 'sort']
        for key in keys:
            if kwargs.get(key, None):
                query_string.append(key + '=' + str(kwargs.get(key, '')))

        url = '/' + module
        if kwargs.get("method", None):
            url += '/' + kwargs.get("method")

        url += '?' + '&'.join(query_string)

        return url

    def check_module_permission(self, permission_type, handler):
        user = handler.context.user

        if [p for p in user.get('panel', {}).get('permissions') if re.match(p, permission_type)]:
            return True

        raise errors.FError(
            err_code='NotAllowedAction',
            err_msg='Not Allowed Action',
            status_code=403
        )

    def check_content_permission(self, user, content, permission_type):

        user_id = str(user.get('_id'))
        permissions_list = content['panel_access'].get(user_id, {}).get('permissions', '')
        if not content.get('panel_access') or not permission_type in permissions_list:
            raise errors.FError(
                err_msg="Not Access For Content",
                err_code="errors.NotAccess",
                status_code=403
            )

        return True
