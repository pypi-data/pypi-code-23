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
import json
from io import open

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8000
DEFAULT_VERSION = 'v2'
DEFAULT_SSL = False
DEFAULT_VERIFY_SSL_CERT = True


class Config(object):
    """Use to specify HTTP connection configurations to be used by clients.
    
    :param token: The Cortex JWT token to make requests that require it. 
    :param host: The host where CORTEX can be reached (e.g., 'localhost')
    :param port: The TCP port. Default is 8000
    :param ssl: True | False
    :param verify_ssl_cert: True | False
    :param version: The version of the CORTEX REST API. Default is v2.
    """

    def __init__(self, 
                 token=None,
                 host=DEFAULT_HOST, 
                 port=DEFAULT_PORT,
                 ssl=DEFAULT_SSL, 
                 verify_ssl_cert=DEFAULT_VERIFY_SSL_CERT,
                 version=DEFAULT_VERSION):
        self.auth_token = token
        self.host = host
        self.port = port
        self.version = version
        self.ssl = ssl
        self.verify_ssl_cert = verify_ssl_cert

