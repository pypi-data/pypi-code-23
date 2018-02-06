import requests
import json
import hvac
from autologging import logged, traced

@logged
@traced
class VaultGatekeeper:
    def request_temp_vault_token(self):
        """Requests temporary vault token from vault-gatekeeper-mesos service"""
        data = {
            'task_id': self.task_id
        }
        request = requests.post(self.gatekeeper_addr + '/token',
                                headers={'content-type': 'application/json'},
                                data=json.dumps(data))
        self.__log.debug("temp token response: %s", request.json())
        request.raise_for_status()
        self.__log.debug("Received temp token: %s", request.json()['token'])
        #couldnt mock json() so did it manually
        return json.loads(request.text)['token']


    def vault_connection(self):
        """Connect to vault without token"""
        client = hvac.Client(url=self.vault_addr)
        return client

    def vault_token_connection(self):
        """Connect to vault with token"""
        client = hvac.Client(url=self.vault_addr, token=self.vault_token)
        return client

    def unwrap_vault_token(self):
        """unwrap a response token"""
        client = self.vault_connection()
        result = client.unwrap(self.temp_vault_token)
        self.__log.debug("unwrap vault response: %s", result)
        return result['auth']['client_token']

    def get_secret_keys(self):
        """Get list of secret keys in specified path"""
        secret_keys = []
        client = self.vault_token_connection()

        self.__log.debug("raw keys from vault: %s", client.list(self.secret_path))
        self.__log.debug("received keys from vault: %s", client.list(self.secret_path)['data']['keys'])

        for secret_key in client.list(self.secret_path)['data']['keys']:
            secret_keys.append(secret_key)

        return secret_keys

    def build_secrets_dict(self):
        """Build the secrets dict to output"""

        values_dict = {}
        client = self.vault_token_connection()

        for secret_key in self.secret_keys:
            full_secret_path = self.secret_path + '/' + secret_key
            values_dict[secret_key] = {}

            for key, value in client.read(full_secret_path)['data'].items():
                values_dict[secret_key][key] = value
                self.__log.debug("adding key: %s with value: %s to dict", key, value)

        return values_dict

    def Client(self):
        """Wrapper function to invoke everything"""

        self.vault_client = self.vault_connection()
        self.temp_vault_token = self.request_temp_vault_token()
        self.vault_token = self.unwrap_vault_token()
        self.secret_keys = self.get_secret_keys()
        self.secrets = self.build_secrets_dict()


    def __init__(self,
                 task_id=None,
                 vault_addr=None,
                 gatekeeper_addr=None,
                 secret_path=None):
        """
        Create the Vaultkeeper service.
        :param task_id: The Mesos task ID for this process' context.
        :param vault_addr: The address for the Vault server.
        :param gatekeeper_addr: The address for the Gatekeeper server.
        :param secret_path: The path to the location of the secrets
        """

        self.task_id = task_id
        self.vault_addr = vault_addr
        self.gatekeeper_addr = gatekeeper_addr
        self.secret_path = secret_path
