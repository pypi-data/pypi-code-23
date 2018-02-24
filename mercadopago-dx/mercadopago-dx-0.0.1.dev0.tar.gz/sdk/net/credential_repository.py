# -*- coding: utf-8 -*-
from sdk.internal import Validator


class CredentialRepository(object):

    def __init__(self, net_client, credential):
        super(CredentialRepository, self).__init__()
        self.credential = credential
        self.net_client = net_client

    def get_access_token(self):
        Validator.validate_non_none(self.credential)
        r = self.net_client.post('/oauth/token', self.credential.as_payload())
        print(r.text)
        if r.status_code == 200:
            response = r.json()
            return response
        else:
            raise Exception('Can not retrieve the \"access_token\"')
