"""
Zookeeper Module for ZK management.
"""
import json
import logging

from aiozk import ZKClient, exc, RetryPolicy
from aiozk.states import States

from ..config import Config
from ..connections.base import Base


class Zookeeper(Base):
    """Zookeeper class

    Singleton class for Zookeeper management.
    """
    __instance = None

    def __init__(self, name: str, server: str, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)

        self._server = server
        self._client = ZKClient(self._server, retry_policy=RetryPolicy.n_times(3))
        self._logger = logging.getLogger(__name__)

    async def start(self):
        """
        Start a Zookeeper client and connects to the server

        Returns:

        """
        await self._client.start()

        if self._client.session.state.current_state == States.CONNECTED:
            self._logger.info("Zookeeper client successfully started.")
        else:
            self._logger.critical("Connection to Zookeper is failed.")
            exit(255)

    async def create_endpoints(self, endpoints: dict):
        """
        Creates ZK zNodes based on the given endpoints.
        Args:
            endpoints (dict): key: url, value: methods

        Returns:

        """
        if not self._client.session.state.current_state == States.CONNECTED:
            await self.start()

        service_name = Config().get_service_conf()['name']
        try:
            await self._client.create('/adminsch', data=b'')
        except exc.NodeExists:
            pass

        for endpoint, methods in endpoints.items():
            url = '/adminsch' + endpoint
            data = bytes(json.dumps({'service': service_name,
                                     'methods': methods
                                    }
                                   ),
                         encoding='ascii')
            try:
                await self._client.create(url, data=data)
                self._logger.info("%s REST endpoint is registered to Zookeeper.", endpoint)
            except exc.NodeExists:
                node_data = await self.get_data(url)

                change = False
                if node_data['service'] != service_name:
                    self._logger.error("Overwrite service for url %s, new service: %s", endpoint, service_name)
                    change = True

                if node_data['service'] != methods:
                    self._logger.info("Updating methods for url %s, new method(s): %s", endpoint, methods)
                    change = True

                if change:
                    await self._client.set_data(url, data=data, force=True)

    async def get_data(self, path: str, *args, **kwargs):
        r"""
        Json parser wrapper over the aiozk client's get_data

        Args:
            path (str): zNode path
            *args: pass to aiozk client
            **kwargs: pass to aiozk client

        Returns:
            zNode data with Python types
        """
        node_data_raw = await self._client.get_data(path, *args, **kwargs)
        data = node_data_raw.decode('utf-8')
        if data:
            return json.loads(data)

    async def cleanup_endpoints(self, service_name: str, endpoints: list):
        """
        Check every zNode (BFS) and if the give service is reposible for that endpoint and
         the endpoint is no longer provided than it will be deleted.
        Args:
            service_name (str): name of the service
            endpoints (list): list of endpoint names

        Returns:

        """
        if not self._client.session.state.current_state == States.CONNECTED:
            await self.start()

        visited = set()
        queue = ['/adminsch']
        while queue:
            current_znode = queue.pop(0)
            if current_znode not in visited:
                try:
                    data = await self.get_data(current_znode)
                except exc.NoNode:
                    if current_znode == '/adminsch':
                        return
                    raise

                if data is not None and data['service'] != service_name and current_znode not in endpoints:
                    await self._client.delete(current_znode, force=True)
                    self._logger.warning("%s endpoint is deleted because it was registed for service %s but no longer "
                                         "provided.", current_znode, service_name)

                visited.add(current_znode)
                for child in await self._client.get_children(current_znode):
                    queue.append(current_znode + '/' + child)

    async def close(self):
        """
        Disconnects from the Zookeeper server
        Returns:

        """
        await self._client.close()
