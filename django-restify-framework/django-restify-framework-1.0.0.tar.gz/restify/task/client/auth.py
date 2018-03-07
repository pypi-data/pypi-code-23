# coding: utf-8

from requests import Request


class AuthBase:
    def __init__(self, username: str, token: str):
        self._username = username
        self._token = token

    def inject_credentials(self, request: Request):
        raise NotImplementedError('Subclass must implement this')


class HeaderAuth(AuthBase):
    def __init__(self, username: str, token: str):
        super().__init__(username, token)

        self._header = 'apikey {username}:{token}'.format(
            username=self._username,
            token=self._token
        )

    def inject_credentials(self, request: Request):
        request.headers['Authorization'] = self._header
