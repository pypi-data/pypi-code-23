from directory_client_core.base import BaseAPIClient

from directory_api_external.supplier import SupplierAPIClient


class DirectoryAPIExternalClient(BaseAPIClient):

    endpoints = {
        'ping': 'healthcheck/ping/',
    }

    def __init__(self, base_url=None, api_key=None):
        self.supplier = SupplierAPIClient(base_url, api_key)
        super().__init__(base_url, api_key)

    def ping(self):
        return self.get(url=self.endpoints['ping'])
