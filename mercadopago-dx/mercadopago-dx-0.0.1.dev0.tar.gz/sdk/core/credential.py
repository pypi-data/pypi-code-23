# -*- coding: utf-8 -*-
class Credential(object):

    def __init__(self, client_id, client_secret):
        super(Credential, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret

    def as_payload(self):
        return {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
