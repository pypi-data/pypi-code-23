import requests
import os
import json as JSON

from datetime import datetime, timedelta

class CrowdCurio(object):
    _client = None

    _http_headers = {
        'default': {
            'Accept': 'application/vnd.api+json',
        },
        'GET': {
            'Content-Type': 'application/vnd.api+json',
        },
        'PUT': {
            'Content-Type': 'application/vnd.api+json',
        },
        'POST': {
            'Content-Type': 'application/vnd.api+json',
        },
        'DELETE': {
            'Content-Type': 'application/vnd.api+json',
        },
    }

    _endpoint_client_ids = {
        'default': (
            'Al1aocYi6CFVZKODMhe5hXiYOhPubI7lQ9fzEya5'
        ),
        'https://test.crowdcurio.com': (
            'C6Fk4XX5kji1UZZJnvtq3uGJlQFZt41FHgZsFgfX'
        ),
    }

    @classmethod
    def connect(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def client(cls):
        if not cls._client:
            cls._client = cls()
        return cls._client

    def __init__(
        self,
        endpoint='http://127.0.0.1:8000',
        client_id=None,
        client_secret=None,
        redirect_url=None,
        username=None,
        password=None
    ):
        CrowdCurio._client = self

        self.endpoint = endpoint or os.environ.get('CURIO_ENDPOINT')
        self.username = username or os.environ.get('CURIO_USERNAME')
        self.password = password or os.environ.get('CURIO_PASSWORD')
        self.client_secret = client_secret or os.environ.get('CURIO_CLIENT_SECRET')

        if client_id:
            self.client_id = client_id
        elif os.environ.get('CURIO_CLIENT_ID'):
            self.client_id = os.environ.get('CURIO_CLIENT_ID')
        else:
            self.client_id = self._endpoint_client_ids.get(
                self.endpoint,
                self._endpoint_client_ids['default']
            )

        #self.cliend_id = "Al1aocYi6CFVZKODMhe5hXiYOhPubI7lQ9fzEya5"
        #self.client_secret = "JQSL12koR7C0L1CZx1gENhgGPf56txRsW6pBARwACOxP8gzJX8RZ0K7VvzY6B4utpNDkqHdEX9j6n8MBGQNmeo9HGrHRMRIRbW5x7EqHq1exiWjdjQab3KSr9Pjsq6oW"

        self.logged_in = False
        self.bearer_token = None

        self.session = requests.session()

    def http_request(
        self,
        method,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        _headers = self._http_headers['default'].copy()
        _headers.update(self._http_headers[method])
        _headers.update(headers)
        headers = _headers

        token = self.get_bearer_token()

        if self.logged_in:
            headers.update({
                'Authorization': 'Bearer %s' % token,
            })

        if etag:
            headers.update({
                'If-Match': etag,
            })

        if "http" in path:
            url = path
        elif endpoint:
            url = endpoint + '/' + path
        else:
            url = self.endpoint + '/api' + path

        if method != 'GET':
            url += '/'
        elif 'format=vnd.api%2Bjson' not in url:
            url += '?format=vnd.api%2Bjson'

            # remove format from params to prevent the backend from throwing a fit.
            if 'format' in params:
                del params['format']

        response = self.session.request(
            method,
            url,
            params=params,
            headers=headers,
            json=json
        )
        
        if response.status_code >= 400:
            raise CrowdCurioAPIException(
                '{0} Error: {1}'.format(
                    response.status_code, JSON.loads(response.content)['errors'][0]
                )
            )
        return response

    def json_request(
        self,
        method,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        response = self.http_request(
            method,
            path,
            params,
            headers,
            json,
            etag,
            endpoint
        )

        if (
            response.status_code == 204 or
            int(response.headers.get('Content-Length', -1)) == 0 or
            len(response.text) == 0
        ):
            json_response = None
        else:
            json_response = response#.json()
            if 'errors' in json_response:
                raise CrowdCurioAPIException(', '.join(
                    map(lambda e: e.get('message', ''),
                        json_response['errors']
                       )
                ))
            elif 'error' in json_response:
                raise CrowdCurioAPIException(json_response['error'])

        return (json_response, response.headers.get('ETag'))

    def get_request(self, path, params={}, headers={}, endpoint=None):
        return self.http_request(
            'GET',
            path,
            params=params,
            headers=headers,
            endpoint=endpoint
        )

    def get(self, path, params={}, headers={}, endpoint=None):
        return self.json_request(
            'GET',
            path,
            params=params,
            headers=headers,
            endpoint=endpoint
        )

    def put_request(
        self,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        return self.http_request(
            'PUT',
            path,
            params=params,
            headers=headers,
            json=json,
            etag=etag,
            endpoint=None
        )

    def put(
        self,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        return self.json_request(
            'PUT',
            path,
            params=params,
            headers=headers,
            json=json,
            etag=etag,
            endpoint=endpoint
        )

    def post_request(
        self,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        return self.http_request(
            'post',
            path,
            params=params,
            headers=headers,
            json=json,
            etag=etag,
            endpoint=endpoint
        )

    def post(
        self,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        return self.json_request(
            'POST',
            path,
            params=params,
            headers=headers,
            json=json,
            etag=etag,
            endpoint=endpoint
        )

    def delete_request(
        self,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        return self.http_request(
            'delete',
            path,
            params=params,
            headers=headers,
            json=json,
            etag=etag,
            endpoint=None
        )

    def delete(
        self,
        path,
        params={},
        headers={},
        json={},
        etag=None,
        endpoint=None
    ):
        return self.json_request(
            'DELETE',
            path,
            params=params,
            headers=headers,
            json=json,
            etag=etag,
            endpoint=endpoint
        )

    def get_csrf_token(self):
        url = self.endpoint + '/'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        return self.session.get(url, headers=headers).headers['x-csrf-token']

    def get_bearer_token(self):
        if not self.bearer_token or self.bearer_expires < datetime.now():
            grant_type = 'password'

            bearer_data = {
                'grant_type': grant_type,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': self.password
            }

            token_response = self.session.post(
                self.endpoint + '/o/token/',
                bearer_data
            ).json()

            if 'error' in token_response:
                raise CrowdCurioAPIException(token_response['error'])

            self.bearer_token = token_response['access_token']
            if (self.bearer_token and grant_type == 'client_credentials'):
                self.logged_in = True
            if 'refresh_token' in token_response:
                self.refresh_token = token_response['refresh_token']
            else:
                self.refresh_token = None
            self.bearer_expires = (
                datetime.now()
                + timedelta(seconds=token_response['expires_in'])
            )

        self.logged_in = True
        return self.bearer_token

class CrowdCurioObject(object):
    @classmethod
    def url(cls, *args):
        return '/'.join(['', cls._api_slug] + [ a for a in args if a ])

    @classmethod
    def get(cls, path, params={}, headers={}):
        return CrowdCurio.client().get(
            cls.url(path),
            params,
            headers
        )

    @classmethod
    def post(cls, path, params={}, headers={}, json={}):
        return CrowdCurio.client().post(
            cls.url(path),
            params,
            headers,
            json
        )

    @classmethod
    def put(cls, path, params={}, headers={}, json={}):
        return CrowdCurio.client().put(
            cls.url(path),
            params,
            headers,
            json
        )

    @classmethod
    def delete(cls, path, params={}, headers={}, json={}):
        return CrowdCurio.client().delete(
            cls.url(path),
            params,
            headers,
            json
        )

    @classmethod
    def where(cls, **kwargs):
        _id = kwargs.pop('id', '')
        return cls.paginated_results(*cls.get(_id, params=kwargs))

    @classmethod
    def find(cls, _id):
        if not _id:
            return None
        return cls.where(id=_id).next()

    @classmethod
    def paginated_results(cls, response, etag):
        return ResultPaginator(cls, response, etag)

    def __init__(self, raw={}, etag=None):
        self.set_raw(raw, etag)

    def __getattr__(self, name):
        # responses from the server may add hierarchy to the dict; check attributes first.
        if 'attributes' in self.raw:
            try:
                return self.raw['attributes'][name]
            except:
                pass

        # try the first layer
        try:
            return self.raw[name]
        except KeyError:
            if name == 'id':
                return None
            raise AttributeError("'%s' object has no attribute '%s'" % (
                self.__class__.__name__,
                name
            ))

    def __setattr__(self, name, value):
        reserved_names = ('raw', 'links')
        if name not in reserved_names and name in self.raw:
            if name not in self._edit_attributes:
                raise ReadOnlyAttributeException(
                    '{} is read-only'.format(name)
                )
            self.raw[name] = value
            self.modified_attributes.add(name)
        else:
            super(CrowdCurioObject, self).__setattr__(name, value)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            self.id
        )

    def set_raw(self, raw, etag=None):
        self.raw = {}
        self.raw.update(self._savable_dict(include_none=True))
        self.raw.update(raw)
        self.etag = etag
        self.modified_attributes = set()

        if 'links' in self.raw:
            self.links = LinkResolver(self.raw['links'], self)

    def _savable_dict(
        self,
        attributes=None,
        modified_attributes=None,
        include_none=False,
    ):
        if not attributes:
            attributes = self._edit_attributes
        out = []
        for key in attributes:
            if type(key) == dict:
                for subkey, subattributes in key.items():
                    if (
                        subkey == 'links' and
                        hasattr(self, 'links') and
                        modified_attributes and
                        'links' in modified_attributes
                    ):
                        out.append(
                            (subkey, self.links._savable_dict(subattributes))
                        )
                    else:
                        out.append((subkey, self._savable_dict(
                            attributes=subattributes,
                            include_none=include_none
                        )))
            elif modified_attributes and key not in modified_attributes:
                continue
            else:
                value = self.raw.get(key)
                if value is not None or include_none:
                    out.append((key, value))
        return dict(out)

    def save(self):
        c_id = ''
        if not self.id:
            save_method = CrowdCurio.client().post
            c_id = None
        else:
            save_method = CrowdCurio.client().put
            c_id = self.id

        if self._api_slug == 'subjectcondition':
            self._api_slug = 'SubjectCondition'
        elif self._api_slug == 'experimentconfirmationcode':
            self._api_slug = 'ExperimentConfirmationCode'
        elif self._api_slug == 'tasksessionpolicy':
            self._api_slug = 'TaskSessionPolicy'
        else:
            self._api_slug = self._api_slug.capitalize()

        response, _ = save_method(
            self.url(self.id),
            json={'data': {'type': self._api_slug, 'id': c_id,'attributes': self._savable_dict(
                modified_attributes=self.modified_attributes
            )}},
            etag=self.etag
        )

        self.raw['id'] = JSON.loads(response.content)['data']['id']
        #self.reload()
        return response

    def reload(self):
        reloaded_project = self.__class__.find(self.id)
        self.set_raw(
            reloaded_project.raw,
            reloaded_project.etag
        )

class ResultPaginator(object):
    def __init__(self, object_class, response, etag):
        self.object_class = object_class
        self.set_page(response)
        self.etag = etag

    def __iter__(self):
        return self

    def next(self):
        if self.object_index >= self.object_count:
            if self.next_href:
                # parse the GET parameters into a dict
                params = {}
                if "?" in self.next_href:
                    ps = self.next_href[self.next_href.index('?')+1:].split('&')
                    if ps is not []:
                        for p in ps:
                            params[p.split('=')[0]] = p.split('=')[1]
                    
                if "page" in self.next_href:
                   page = self.next_href.split('page=')[1]
                   self.next_href = self.next_href[:self.next_href.index('?')-1]
                   params['page'] = page
                   response, _ = CrowdCurio.client().get(self.next_href, params=params)
                else:
                    response, _ = CrowdCurio.client().get(self.next_href, params=params)
                self.set_page(response)
            else:
                raise StopIteration

        i = self.object_index
        self.object_index += 1

        if isinstance(self.object_list, list):
            obj = self.object_list[i]
        else:
            obj = self.object_list

        return self.object_class(obj, etag=self.etag)
    
    def __next__(self):
        self.next()

    def set_page(self, response):
        response = JSON.loads(response.content)
        self.meta = response.get('meta', {})
        self.pagination = self.meta.get('pagination', {})
        self.links = response.get('links', {})
        self.meta = self.meta.get(self.object_class._api_slug, {})
        self.page = self.pagination.get('page', 1)
        self.page_count = self.pagination.get('pages', 1)
        self.next_href = self.links.get('next')
        self.object_list = response.get("data", [])
        self.object_count = len(self.object_list)
        self.object_index = 0



class CrowdCurioAPIException(Exception):
    pass

class ReadOnlyAttributeException(Exception):
    pass
