"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

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
from typing import Dict

import requests

from .config import Config


class ServiceConnector:

    __defaultHeaders = {} # type: Dict[str, str]

    def __init__(self, config=Config()):
        if not isinstance(config, Config):
            raise TypeError(u'parameter should be of type Config')
        self.__connectionConfig = config

    ## properties ##

    @property
    def protocol(self):
        return u'https' if self.__connectionConfig.ssl else u'http'

    @property
    def base_url(self):
        port = ':{}'.format(self.__connectionConfig.port) if \
                self.__connectionConfig.port else ''
        return u'{0}://{1}{2}/{3}'.format(
            self.protocol,
            self.__connectionConfig.host,
            port,
            self.__connectionConfig.version)

    ## methods ##

    def post_file(self, uri, files, data, headers=None):
        headersToSend = self._construct_headers(headers)
        url = self._construct_url(uri)
        return requests.post(url, files=files, data=data, headers=headersToSend,
                             verify=self.__connectionConfig.verify_ssl_cert)

    def request(self, method, uri, body=None, headers=None, **kwargs):
        headersToSend = self._construct_headers(headers)
        url = self._construct_url(uri)
        return requests.request(method, url, data=body, headers=headersToSend,
                                verify=self.__connectionConfig.verify_ssl_cert, **kwargs)

    @staticmethod
    def urljoin(pieces):
        pieces = [_f for _f in [s.rstrip('/') for s in pieces] if _f]
        return '/'.join(pieces)

    ## private ##

    def _construct_url(self, uri):
        return self.urljoin([self.base_url, uri])

    def _construct_headers(self, headers):
        headersToSend = self.__defaultHeaders.copy()

        if self.__connectionConfig.auth_token:
            token = 'Bearer {}'.format(self.__connectionConfig.auth_token)
            headersToSend[u'Authorization'] = token

        if headers is not None:
            headersToSend.update(headers)
        return headersToSend
