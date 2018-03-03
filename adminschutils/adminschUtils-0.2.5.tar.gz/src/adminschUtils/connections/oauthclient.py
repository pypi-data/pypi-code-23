import asyncio
import aiohttp
from typing import TypeVar

from.httpclient import HTTPClient

O = TypeVar('T', bound='OAuthClient')


class OAuthClient(HTTPClient):
    def __init__(self, name, server, resource_server, credentials, *args, **kwargs):
        super(OAuthClient, self).__init__(name=name, url=resource_server, *args, **kwargs)

        self.server = server
        self.credentials = credentials
        self.resource_server_url = resource_server['url']

        self._token = None
        self.active = True

        self.logger.debug("OAuth client %s is initialized.", name)

    async def refresh_token(self):
        """
        Periodically refreshing the oAuth token by adding itself to the event loop.
        Returns:

        """
        auth = aiohttp.BasicAuth(self.credentials['client_id'], self.credentials['client_secret'])
        with aiohttp.ClientSession(auth=auth, conn_timeout=10) as client:
            data = {'grant_type': self.credentials['grant_type'],
                    'username': self.credentials['username'],
                    'password': self.credentials['password'],
                    'scope': self.credentials['scope'],
                   }
            response = await client.post(url=self.server, data=data)
            response = await response.json()
        if 'error' in response:
            self.logger.error("Invalid credentials for %s", self.name)
            self.logger.error("Disable this client!")
            self.active = False

        self._token = response['access_token']
        delay = float(response['expires_in']) * 0.8
        self.logger.info("Token is renewed, next renew will be in %s seconds.", delay)

        loop = asyncio.get_event_loop()
        loop.call_later(delay, self.refresh_token())

    @property
    def token(self) -> str:
        """
        Getter for the oAuth token
        Returns:
            Token
        """
        return self._token

    async def request_data(self, token: str):
        """
        It validate the token and get all of the data from the resource server.
        Args:
            token: clients' token

        Returns:
            Data from resourse server
        """
        url = self.resource_server_url + token
        data = await self.get(url)
        if 'error' in data:
            self.logger.error("%s", data['error_description'])
            return
        return data
