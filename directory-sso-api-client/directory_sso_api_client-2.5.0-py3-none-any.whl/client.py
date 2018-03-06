from directory_client_core.base import BaseAPIClient

from directory_sso_api_client.user import UserAPIClient


class DirectorySSOAPIClient(BaseAPIClient):

    endpoints = {
        'ping': 'api/v1/healthcheck/ping/',
    }

    def __init__(self, base_url=None, api_key=None):
        super(DirectorySSOAPIClient, self).__init__(base_url, api_key)
        self.user = UserAPIClient(base_url, api_key)

    def ping(self):
        return self.get(url=self.endpoints['ping'])
