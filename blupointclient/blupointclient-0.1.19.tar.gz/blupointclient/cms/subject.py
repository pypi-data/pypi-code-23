from blupointclient.cms import components_base

class BlupointCmsSubject(components_base):

    def __init__(self, settings):
        super(BlupointCmsSubject, self).__init__(settings)
        self.settings = settings

    async def get(self, id, **kwargs):
        self.set_token(kwargs.get("token", None))

        return await self._get('/subjects/{0}'.format(id))

    async def put(self, id, **kwargs):
        self.set_token(kwargs.get("token", None))

        return await self._put('/subjects/' + id, kwargs.get("params", {}))

    async def update(self, id, document, **kwargs):
        self.set_token(kwargs.get("token", None))

        existing_user = await self.get(id)
        existing_user['panel'].update(document)

        updated_user = await self._put('/subjects/' + existing_user['_id'], existing_user)

        return updated_user

    async def delete(self, id, **kwargs):
        self.set_token(kwargs.get("token", None))

        existing_user = await self.get(id)
        existing_user.update({
            'panel': {},
            'is_panel_user': False
        })

        updated_user = await self._put('/subjects/' + existing_user['_id'], existing_user)

        return updated_user