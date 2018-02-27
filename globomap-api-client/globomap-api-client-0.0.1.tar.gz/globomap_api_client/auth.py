"""
   Copyright 2018 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import json

import requests

from globomap_api_client import GLOBOMAP_API_ADDRESS


class Auth(object):

    def __init__(self, api_url, username, password):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.generate_token()

    def generate_token(self):
        res = self._make_request()
        self.token = res['token']['id']

    def _make_request(self):
        url = '{}/v2/auth'.format(self.api_url)
        data = {
            'username': username,
            'password': password
        }
        res = request.post(url, data=json.dumps(data))
        if res.status_code == 200:
            return res.json()
