import json
from aiozk import ZKClient
from aiozk.exc import NoNode, NodeExists
from aiozk.protocol import AuthRequest
from vmshepherd.runtime import AbstractRuntimeData


class ZookeeperDriver(AbstractRuntimeData):

    def __init__(self, instance_id, config):
        super().__init__(instance_id)
        self.reconfigure(config)

    def set_auth(self, addauth):
        if addauth is not None:
            self._auth = {
                'scheme': addauth.get('scheme', 'digest'),
                'auth': addauth.get('auth', 'vmshepherd:vmshepherd'),
            }
        else:
            self._auth = None

    async def _assure_connected(self):
        if self._zk is None:
            self._zk = ZKClient(servers=self._servers, chroot=self._working_path)
        await self._zk.start()
        if self._auth is not None:
            auth_req = AuthRequest(type=0, **self._auth)
            await self._zk.send(auth_req)

    def reconfigure(self, config):
        if isinstance(config['servers'], str):
            self._servers = ','.join(config['servers'])
        else:
            self._servers = config['servers']
        self._working_path = config.get('working_path', '/vmshepherd')
        self.set_auth(config.get('addauth'))
        self._zk = None

    async def _set_preset_data(self, preset_name, data):
        await self._assure_connected()
        prepared_data = json.dumps(data)
        try:
            await self._zk.set_data(preset_name, prepared_data)
        except NoNode:
            await self._zk.create(preset_name)
            await self._zk.set_data(preset_name, prepared_data)

    async def _get_preset_data(self, preset_name):
        await self._assure_connected()
        try:
            res = await self._zk.get_data(preset_name)
        except NoNode:
            return {}
        return json.loads(res.decode('utf-8'))

    async def _acquire_lock(self, name):
        try:
            await self._zk.create(f'{name}.lock')
            return True
        except NodeExists:
            return False

    async def _release_lock(self, name):
        try:
            await self._zk.delete(f'{name}.lock')
            return True
        except NoNode:
            return False
