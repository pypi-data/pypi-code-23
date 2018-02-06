import unittest
#have to do this for py27 compatibility
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from vault_gatekeeper_client import *

class VaultGatekeeperTestCase(unittest.TestCase):
    """Test cases for the VaultGatekeeper class"""

    @patch('requests.post')
    def test_request_temp_token(self, mock_requests):
        """Tests request_temp_token function"""
        mock_requests.return_value.text = json.dumps({"token": "abc123"})
        gatekeeper = VaultGatekeeper(task_id='test_app_id',
                                     gatekeeper_addr='https://vault-gatekeeper',
                                     vault_addr='https://vault-server:8200',
                                     secret_path='secret/test')

        self.assertEqual(gatekeeper.request_temp_vault_token(), 'abc123')

    @patch('hvac.Client.unwrap')
    def test_request_unwrap_token(self, mock_requests):
        """Tests unwrap_token function"""
        mock_requests.return_value = {'request_id': '64bc8be3-0415-670f-bf84-465ad33756fb',
                                      'auth': {
                                          'client_token': '3b243bd0-db25-b0d3-xfxf-0a01b88cdf75',
                                          'accessor': 'xf7d7abc-78d1-6e69-99e5-2269d20fc8c1',
                                          'policies': ['test', 'default']
                                          }
                                     }

        gatekeeper = VaultGatekeeper(task_id='test_app_id',
                                     gatekeeper_addr='https://vault-gatekeeper',
                                     vault_addr='https://vault-server:8200',
                                     secret_path='secret/test')
        gatekeeper.temp_vault_token = "temp_vault_token123"

        self.assertEqual(gatekeeper.unwrap_vault_token(), '3b243bd0-db25-b0d3-xfxf-0a01b88cdf75')

    @patch('hvac.Client.list')
    def test_get_secret_keys(self, mock_hvac_client_list):
        """Tests get_secret_keys function"""
        mock_hvac_client_list.return_value = {'data': {'keys': ['key1', 'key2', 'key3']}}

        gatekeeper = VaultGatekeeper(task_id='test_app_id',
                                     gatekeeper_addr='https://vault-gatekeeper',
                                     vault_addr='https://vault-server:8200',
                                     secret_path='secret/test')
        gatekeeper.vault_token = "temp_vault_token123"
        self.assertEqual(gatekeeper.get_secret_keys(), ['key1', 'key2', 'key3'])

    @patch('hvac.Client.read')
    def test_build_secrets_dict(self, mock_hvac_client_read):
        """Tests build_secrets_dict function"""
        mock_hvac_client_read.return_value = {'data': {'key1':'data1', 'key2':'data2'}}

        gatekeeper = VaultGatekeeper(task_id='test_app_id',
                                     gatekeeper_addr='https://vault-gatekeeper',
                                     vault_addr='https://vault-server:8200',
                                     secret_path='secret/test')
        gatekeeper.vault_token = "temp_vault_token123"
        gatekeeper.secret_keys = ['key1']

        self.assertEqual(gatekeeper.build_secrets_dict(),
                         {'key1': {'key1':'data1', 'key2':'data2'}}
                        )

if __name__ == '__main__':
    '''
    #debug messages are nice sometimes
    logging.basicConfig(
         level=logging.DEBUG, stream=sys.stdout,
         format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    '''
    unittest.main()
