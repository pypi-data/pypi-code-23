import http
from unittest.mock import patch, MagicMock

from requests import Response

from directory_api_external.client import DirectoryAPIExternalClient


class DummyDirectoryAPIExternalClient(DirectoryAPIExternalClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch.object(self.supplier, 'send', self.send).start()

    @patch('requests.Session.send')
    def send(self, mock_send, *args, **kwargs):
        response = Response()
        response.status_code = http.client.BAD_REQUEST
        response.json = lambda: MagicMock()
        mock_send.return_value = response
        return super().send(*args, **kwargs)
