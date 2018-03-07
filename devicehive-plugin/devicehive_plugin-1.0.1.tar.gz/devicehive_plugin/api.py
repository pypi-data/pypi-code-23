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


from devicehive_plugin.message import RequestMessage
from devicehive_plugin.token import Token

__all__ = ['Api']


class Api(object):

    def __init__(self, transport, credentials, topic_name):
        self._transport = transport
        self._token = Token(self, credentials, topic_name)
        self._topic_name = topic_name
        self._connected = True

    @property
    def connected(self):
        return self._connected

    @property
    def transport(self):
        return self._transport

    def authenticate(self):
        self._token.auth()

    def subscribe(self):
        request = RequestMessage(self, RequestMessage.TOPIC_TYPE,
                                 RequestMessage.SUBSCRIBE_ACTION)
        request.set_payload('t', [self._topic_name])
        return request.execute()

    def unsubscribe(self):
        request = RequestMessage(self, RequestMessage.TOPIC_TYPE,
                                 RequestMessage.UNSUBSCRIBE_ACTION)
        request.set_payload('t', [self._topic_name])
        return request.execute()

    def disconnect(self):
        self._connected = False
        if not self._transport.connected:
            return
        self._transport.disconnect()
