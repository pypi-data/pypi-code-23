import http
from unittest.mock import patch, MagicMock

from requests import Response

from directory_api_client.client import DirectoryAPIClient


class DummyDirectoryAPIClient(DirectoryAPIClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch.object(self.enrolment, 'send', self.send).start()
        patch.object(self.supplier, 'send', self.send).start()
        patch.object(self.company, 'send', self.send).start()
        patch.object(self.buyer, 'send', self.send).start()
        patch.object(self.notifications, 'send', self.send).start()
        patch.object(self.exportopportunity, 'send', self.send).start()
        patch.object(self.exportreadiness, 'send', self.send).start()

    @patch('requests.Session.send')
    def send(self, mock_send, *args, **kwargs):
        response = Response()
        response.status_code = http.client.BAD_REQUEST
        response.json = lambda: MagicMock()
        mock_send.return_value = response
        return super().send(*args, **kwargs)
