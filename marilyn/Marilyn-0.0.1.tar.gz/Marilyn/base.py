import json

import requests

from .exceptions import *


class CoreApi:
    def __init__(self, login=None, password=None, api_key=None, url_api=None):
        if url_api is None:
            url_api = "https://app.mymarilyn.ru/"

        self.login = login
        self.password = password
        self.api_key = api_key
        self.url_api = url_api

        self.header = {
            "Accept": "application/json",
            "X-API-Token": self.api_key,
        }

        self.http = requests.Session()
        self.http.headers.update({"Accept": "application/json"})
        if api_key is not None:
            self.http.headers.update({"X-API-Token": self.api_key, })

    def _login(self):
        """
        Login user -> get new API Token

        http put to auth, send login and password,
        response to json (token and live time)
        """
        data = {
            "email": self.login,
            "password": self.password,
            "ttl": 180
        }

        req = self.http.put(url=self.url_api + 'auth', json=data)

        if req.status_code != 200:
            raise LoginRequired('status code is not 200')

        req_json = req.json()
        if req_json.get('token') is not None:
            self.api_key = req_json['token']
            self.http.headers.update({"X-API-Token": self.api_key, })
        else:
            raise LoginRequired('api key is None')

    def auth(self):
        """
        test auth users and get new api_key or use old api_key
        :return: None
        """
        if not self.login:
            raise LoginRequired('Login is required to auth')

        if not self.password and not self.api_key:
            raise LoginRequired('password and api_key is None')

        if self.api_key:
            req = self.http.get(self.url_api + 'me')
            if req.status_code == 200:
                req_json = req.json()
                if self.login == req_json['email']:
                    return
                else:
                    raise LoginRequired('login is no equal email')
            else:
                raise LoginRequired('login or password is not correct (maubi error api)')
        else:
            self._login()

    def get_api(self):
        return MarilynApiMethod(self)

    def method(self, method, values=None):
        if self.http.headers.get("X-API-Account"):
            del self.http.headers["X-API-Account"]

        if values.get('x_api_acoount'):
            self.http.headers.update({
                "X-API-Account": str(values['x_api_acoount'])
            })
            del values['x_api_acoount']
        req = self.http.get(self.url_api + str(method), params=values)
        if req.status_code == 200:
            try:
                req_json = req.json()
            except json.decoder.JSONDecodeError:
                raise MethodReturn('return text is not JSON, text: {}'.format(req.text))
            return req_json
        else:
            raise MethodReturn('status code is not 200, info: {}'.format(req.text))


class MarilynApiMethod(object):
    __slots__ = ('_merilyn', '_method')

    def __init__(self, merilyn, method=None):
        self._merilyn = merilyn
        self._method = method

    def __getattr__(self, method):
        if '_' in method:
            m = method.split('_')
            method = m[0] + ''.join(i.title() for i in m[1:])

        return MarilynApiMethod(
            self._merilyn,
            (self._method + '/{}' if method == 'id' else ((self._method + '/' if self._method else '') + method))
        )

    def __call__(self, **kwargs):
        if kwargs.get('api_id_list'):
            self._method = self._method.format(*kwargs['api_id_list'])
            del kwargs['api_id_list']
        return self._merilyn.method(self._method, kwargs)
