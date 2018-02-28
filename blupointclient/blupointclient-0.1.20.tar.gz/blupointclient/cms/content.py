import asyncio
import slugify
from flasky import errors
from blupointclient.cms import components_base
from quark_utilities import temporal_helpers



class BlupointCmsContent(components_base):

    def __init__(self, settings):
        super(BlupointCmsContent, self).__init__(settings)
        self.settings = settings

    async def get(self, id=None, slug=None, **kwargs):
        params = self.prepare_query(kwargs)
        user_id = None
        if params.get("user", None):
            user_id = str(params.get("user",{}).get('_id', None))

        self.set_token(kwargs.get("token", None))
        # 'panel_access.' + str(params['user']['_id']) + '.permissions': "read",
        if id:
            self.update_filters(params['document'], {
                '_id': str(id)
            })
        elif slug:
            self.update_filters(params['document'], {
                'url': str(slug)
            })
        url = self.prepare_endpoint("contents", "_query",
                                    skip=0,
                                    limit=1,
                                    sort=None)

        response = await self._post(url, params['document'])

        items = response['data']['items']
        count = response['data']['count']

        if len(items) == 0:
            raise errors.FError(
                    err_msg='Not Exist Content',
                    err_code='ResorceNotFound',
                    status_code=404
            )

        """ will be used later for get_user_content
        content = items[0]
        if not content.get('panel_access') or not content['panel_access'].get(user_id) or\
                        not 'read' in content['panel_access'][user_id].get('permissions'):
            raise errors.FError(
                    err_msg='Not Access For Content',
                    err_code='NotAccessForContent',
                    status_code=403
            )"""

        relation_tasks = []

        for item in items:
            relation_tasks.append(self.expand_content_field(item))
        await asyncio.gather(*relation_tasks)

        return items, count

    async def create(self, **kwargs):
        params = self.prepare_query(kwargs)
        user_id = str(params.get("user", {}).get('_id'))

        tags = [{'tag': x, 'slug': slugify.slugify(x)} for x in params['document']['tags']]
        if params['document'].get('type', None) == 'channel':
            collections = [{'tag': x, 'slug': slugify.slugify(x)} for x in params['document'].get('collections',[])]
            params['document']['collections'] = collections
        else:
            params['document'].pop('collections', None)

        self.update_attributes(params['document'], {
                'panel_access': {
                    user_id: {
                        'permissions': ['read', 'update', 'delete']
                    }
                },
                'tags': tags,
                'status': params['document'].get('status', 'draft'),
                'start_date': temporal_helpers.utc_now(),
                'base_type': 'content',
                'panel_sys': {
                    'created_at': temporal_helpers.utc_now(),
                    'created_by': user_id
                }
            })

        created = await self._post('/contents', params['document'])

        if params['document'].get('status') == 'active':
            published_content_body = {
                '_id': created['_id']
            }

            await self._post('/published-contents', published_content_body)

        return created

    async def update(self, id, **kwargs):
        params = self.prepare_query(kwargs)
        user = params.get("user", {})

        exist_content,count = await self.get(id, **params)

        if not exist_content:
            raise errors.FError(
                err_msg="Content Does Not Exist in CMS",
                err_code="errors.ResourceNotFound",
                status_code=404
            )
        exist_content = exist_content[0]



        if params['document'].get('tags'):
            tags = [{'tag': x, 'slug': slugify.slugify(x)} for x in params['document']['tags']]

            self.update_attributes(params['document'], {'tags': tags})

        if params['document'].get('collections', None):
            collections = [{'name': x, 'slug': slugify.slugify(x)} for x in params['document']['collections']]
            params['document']['collections'] = collections

            params['document']['type'] = exist_content['type']

        if not exist_content.get('panel_sys'):
            exist_content['panel_sys'] = {}

        self.update_attributes(exist_content['panel_sys'], {
            'modified_at': temporal_helpers.utc_now(),
            'modified_by': str(user.get('_id'))
        })

        params['document'].pop('panel_access', None)

        updated = await self._put('/contents/{}'.format(id), params['document'], exist_content['sys']['version'])

        """if params['document']['status'] == 'active':
            published_content_body = {
                '_id': id
            }

            await self._post('/published-contents', published_content_body, exist_content['sys']['version'])

        elif params['document']['status'] != 'active':
            try:
                await self._delete('/published-contents/{}'.format(id))
            except errors.FError:
                #: Content is not published so we can swallow exception
                pass"""


        if not updated
            raise errors.FError(
                err_msg="Error updating content in CMS",
                err_code="errors.BackendError",
                status_code=504
            )

        return updated

    async def delte(self, id, **kwargs):
        params = self.prepare_query(kwargs)
        user = params.get("user", {})

        exist_content = await self.get(id, **params)

        if not exist_content:
            raise errors.FError(
                err_msg="Content Does Not Exist in CMS",
                err_code="errors.ResourceNotFound",
                status_code=404
            )

        if self.check_content_permission(user, exist_content, 'delete'):

            if exist_content['base_type'] == 'folder':
                await self._post('/folder-operations'.format(id),
                                   {
                                       "folder_id": str(exist_content['_id']),
                                       "operation_name": "remove",
                                       "operation_parameters": {
                                           "apply_to_child_folders": False
                                       }
                                   })
            else:
                await self._delete('/contents/{0}'.format(id), {'type': exist_content['type']})