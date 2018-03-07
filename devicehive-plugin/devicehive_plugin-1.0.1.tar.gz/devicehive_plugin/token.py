# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import datetime
import requests

from devicehive_plugin.error import AuthApiError, TokenError
from devicehive_plugin.message import RequestMessage


class Token(object):

    AUTH_HEADER_NAME = 'Authorization'
    AUTH_HEADER_PREFIX = 'Bearer '
    SUCCESS_CODES = [200, 201, 204]

    def __init__(self, api, credentials, topic_name):
        self._api = api
        self._topic_name = topic_name
        self._login = credentials.get('login')
        self._password = credentials.get('password')
        self._refresh_token = credentials.get('refresh_token')
        self._access_token = credentials.get('access_token')
        self._plugin_refresh_token = credentials.get('plugin_refresh_token')
        self._plugin_access_token = credentials.get('plugin_access_token')
        auth_url = credentials.get('auth_url')
        if auth_url and not auth_url.endswith('/'):
            auth_url += '/'
        self._auth_url = auth_url

    @property
    def _auth_header(self):
        auth_header_name = self.AUTH_HEADER_NAME
        auth_header_value = self.AUTH_HEADER_PREFIX + self._access_token
        return {auth_header_name: auth_header_value}

    def _request(self, method, url, params=None, data=None, headers=None):
        url = self._auth_url + url
        response = requests.request(method, url, params=params, json=data,
                                    headers=headers)
        content = response.json()
        if response.status_code in self.SUCCESS_CODES:
            return content

        raise AuthApiError(response.status_code, content['message'])

    def _auth_request(self, method, url, params=None, data=None, headers=None):
        if headers is None:
            headers = {}

        headers.update(self._auth_header)
        try:
            return self._request(method, url, params, data, headers)
        except AuthApiError as auth_api_error:
            if auth_api_error.code != 401:
                raise

        if self._refresh_token:
            self._refresh_user_token()
        elif self._login and self._password:
            self._get_user_tokens()
        headers.update(self._auth_header)
        return self._request(method, url, params, data, headers)

    def _auth(self):
        request = RequestMessage(self._api, RequestMessage.PLUGIN_TYPE,
                                 RequestMessage.AUTHENTICATE_ACTION)
        request.set_payload('token', self._plugin_access_token)
        return request.execute()

    def _get_user_tokens(self):
        method = 'POST'
        url = 'token'
        data = {
            'login': self._login,
            'password': self._password,
        }
        tokens = self._request(method, url, data=data)
        self._refresh_token = tokens['refreshToken']
        self._access_token = tokens['accessToken']

    def _get_plugin_tokens(self, expiration=None):
        method = 'POST'
        url = 'token/plugin/create'
        if expiration is None:
            expiration = datetime.datetime.utcnow() + datetime.timedelta(1)
        # The only way to get proper format with all supported python versions.
        expiration = '%s.%.3dZ' % (expiration.strftime('%Y-%m-%dT%H:%M:%S'),
                                   expiration.microsecond//1000)
        data = {
            'a': [0],
            'e': expiration,
            't': 0,
            'tpc': self._topic_name
        }
        tokens = self._auth_request(method, url, data=data)
        self._plugin_refresh_token = tokens['refreshToken']
        self._plugin_access_token = tokens['accessToken']

    def _refresh(self, token):
        method = 'POST'
        url = 'token/refresh'
        data = {
            'refreshToken': token
        }
        tokens = self._request(method, url, data=data)
        return tokens['accessToken']

    def _refresh_user_token(self):
        self._access_token = self._refresh(self._refresh_token)

    def _refresh_plugin_token(self):
        self._plugin_access_token = self._refresh(self._plugin_refresh_token)

    def auth(self):
        if self._plugin_access_token:
            self._auth()
        elif not self._auth_url:
            raise TokenError('Auth url required.')
        elif self._plugin_refresh_token:
            self._refresh_plugin_token()
            self._auth()
        elif self._access_token:
            self._get_plugin_tokens()
            self._auth()
        elif self._refresh_token:
            self._refresh_user_token()
            self._get_plugin_tokens()
            self._auth()
        elif self._login and self._password:
            self._get_user_tokens()
            self._get_plugin_tokens()
            self._auth()
        elif self._login:
            raise TokenError('Password required.')
        elif self._password:
            raise TokenError('Login required.')
