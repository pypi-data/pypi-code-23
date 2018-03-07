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


import six
import time
import logging

from devicehive_plugin.error import TransportError
from devicehive_plugin.transport import Transport


__all__ = ['Plugin']
logger = logging.getLogger(__name__)


class Plugin(object):

    def __init__(self, handler_class, *handler_args, **handler_kwargs):
        self._api_handler_options = {'handler_class': handler_class,
                                     'handler_args': handler_args,
                                     'handler_kwargs': handler_kwargs}
        self._transport = None

    @property
    def handler(self):
        return self._transport.api_handler.handler

    def _ensure_transport_disconnect(self):
        if self._transport.connected:
            self._transport.disconnect()

    def connect(self, proxy_endpoint, topic_name, **options):
        transport_keep_alive = options.pop('transport_keep_alive', True)
        transport_alive_sleep_time = options.pop('transport_alive_sleep_time',
                                                 1e-6)
        connect_timeout = options.pop('connect_timeout', 30)
        max_num_connect = options.pop('max_num_connect', 10)
        connect_interval = options.pop('connect_interval', 1)
        credentials = {'login': options.pop('login', None),
                       'password': options.pop('password', None),
                       'refresh_token': options.pop('refresh_token', None),
                       'access_token': options.pop('access_token', None),
                       'auth_url': options.pop('auth_url', None)}
        api_init = options.pop('api_init', True)
        self._api_handler_options['credentials'] = credentials
        self._api_handler_options['topic_name'] = topic_name
        self._api_handler_options['api_init'] = api_init
        self._transport = Transport(self._api_handler_options)
        if not transport_keep_alive:
            self._ensure_transport_disconnect()
            self._transport.connect(proxy_endpoint, **options)
            return
        connect_time = time.time()
        num_connect = 0
        while True:
            self._ensure_transport_disconnect()
            self._transport.connect(proxy_endpoint, **options)
            while self._transport.is_alive():
                time.sleep(transport_alive_sleep_time)
            exception_info = self._transport.exception_info
            if exception_info:
                if isinstance(exception_info[1], TransportError):
                    logger.error('An error has occurred:',
                                 exc_info=exception_info)
                else:
                    six.reraise(*exception_info)
            if not self.handler.api.connected:
                return
            if time.time() - connect_time < connect_timeout:
                num_connect += 1
                if num_connect > max_num_connect:
                    six.reraise(*exception_info)
                time.sleep(connect_interval)
                continue
            connect_time = time.time()
            num_connect = 0
