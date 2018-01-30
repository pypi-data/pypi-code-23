# -*- coding: utf-8 -*-

"""
cloudcix.auth
~~~~~~~~~~~~~

This module implements the CloudCIX API Client Authentications
"""

import json
import requests

from cloudcix.conf import settings


class TokenAuth(requests.auth.AuthBase):
    """
    CloudCIX Token-based authentication
    """

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['X-Auth-Token'] = self.token
        return request

    def __eq__(self, other):
        return self.token == other.token


class AdminSession:
    """
    Requests wrapper for Keystone authentication using cloudcix credentials
    """

    def __init__(self):
        self.headers = {'content-type': 'application/json'}
        self.auth_url = settings.CLOUDCIX_AUTH_URL
        self.username = settings.CLOUDCIX_API_USERNAME
        self.password = settings.CLOUDCIX_API_PASSWORD
        self.domain = settings.CLOUDCIX_API_KEY

    def get_token(self, **kwargs):
        kwargs['headers'] = self.headers
        response = requests.post(
            self.token_url,
            data=json.dumps(self.data),
            **kwargs
        )
        if response.status_code < 400:
            return response.headers['X-Subject-Token']
        # TODO: not sure if should return entire response, False, or status?
        return response

    @property
    def token_url(self):
        return '{}/auth/tokens'.format(self.auth_url)

    @property
    def data(self):
        return {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": self.username,
                            "password": self.password,
                            "domain": {
                                "id": self.domain
                            }
                        }
                    }
                }
            }
        }


class ActiveDirectoryAuth:
    """
    Provides authentication for active directory backends into CloudCIX

    TODO: Deprecate or migrate to v0.3+ of python-cloudcix
    """

    def __init__(self):
        raise NotImplemented
