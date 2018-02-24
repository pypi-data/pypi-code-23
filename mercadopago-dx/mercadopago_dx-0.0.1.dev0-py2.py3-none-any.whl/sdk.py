from internal import Validator
from net.credential_repository import CredentialRepository
from core import Credential
from net.net_client import NetClient


class Sdk(object):

    def __init__(self, client_id, client_secret):
        """
        Initialize SDK, the operation should be made async
        visit https://www.mercadopago.com/mla/account/credentials
        and select 'Basic checkout' tab
        :param client_id: the client id
        :param client_secret: the client secret
        """
        super(Sdk, self).__init__()
        Validator.validate_non_none(client_id)
        Validator.validate_non_none(client_secret)
        self.net_client = NetClient()
        self.credential_repository = CredentialRepository(self.net_client, Credential(client_id, client_secret))
        self.access_token = self.credential_repository.get_access_token()
        print(self.access_token)
