"""
Minimal HTTP client based on aiohttp.
"""
import asyncio
import aiohttp
import json

from .base import Base


class HTTPClient(Base):
    """
    Inheriting from connections.Base
    It extends the aiohttp client with json handling.
    """
    def __init__(self, name: str, url: str = None, base_url: str = None, *args, **kwargs):
        r"""
        Init method... All of the additional arguments will be pass to the super class.
        Args:
            name(str): name of the instance
            url (str): URL for the client
            *args:
            **kwargs:
        """
        super(HTTPClient, self).__init__(name=name, *args, **kwargs)
        self.client = aiohttp.ClientSession(conn_timeout=10, loop=asyncio.get_event_loop())
        self._url = url
        if base_url is not None:
            self.base_url = base_url
        else:
            self.base_url = ''

    @property
    def url(self):
        return f'{self.base_url}/{self.url}'

    async def get(self, url: str = None, params: dict = None) -> dict:
        """
        Make a HTTP GET for the url with the given params.
        Args:
            url:
            params:

        Returns:
            Returns the date in dictionary.
        """
        endpoint = url or self.url
        async with self.client.get(endpoint, params=params) as response:
            data = await response.text()
            data = json.loads(data)
        return data

    async def post(self, data: dict, url: str = None) -> dict:
        """
        Make a HTTP POST for the url with the given data.
        Args:
            data(dict): this data will be send as post
            url(str): to this url

        Returns:
            Returns a dict as response data from the other end.
        """
        endpoint = url or self.url
        async with self.client.post(endpoint, data=data) as response:
            return await response.json()
