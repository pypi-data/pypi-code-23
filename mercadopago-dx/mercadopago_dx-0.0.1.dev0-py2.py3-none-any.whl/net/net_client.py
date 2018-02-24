# -*- coding: utf-8 -*-
import requests

from sdk.internal import Validator


class NetClient(object):
    DEFAULT_BASE_URL = 'https://api.mercadopago.com'

    def __init__(self, base_url=None):
        super(NetClient, self).__init__()

        self.base_url = NetClient.DEFAULT_BASE_URL if (base_url is None) else base_url

    def get(self, path, payload=None):
        Validator.validate_path(path)
        return requests.get(self.compose(path), params=payload)

    def post(self, path, data=None):
        return requests.post(self.compose(path), data=data)

    def compose(self, path):
        return self.base_url + path
