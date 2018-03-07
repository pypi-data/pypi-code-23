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


from devicehive_plugin.api import Api
from devicehive_plugin.api_event import ApiEvent
from devicehive_plugin.error import ResponseMessageError

__all__ = ['ApiHandler']


class ApiHandler(object):

    def __init__(self, transport, credentials, topic_name, handler_class,
                 handler_args, handler_kwargs, api_init=True):
        self._transport = transport
        self._api = Api(self._transport, credentials, topic_name)
        self._handler = handler_class(self._api, *handler_args,
                                      **handler_kwargs)
        self._api_init = api_init
        self._handle_connect = False

    @property
    def handler(self):
        return self._handler

    def handle_event(self, message):
        if not message.is_notification_type:
            raise ResponseMessageError('An unsupported event received')

        event = ApiEvent(message.payload_message)

        # call global event handler at first
        self._handler.handle_event(event)

        # call action-specific handler
        if event.is_command_insert_event:
            self._handler.handle_command_insert(event.data)
        elif event.is_command_update_event:
            self._handler.handle_command_update(event.data)
        elif event.is_notification_event:
            self._handler.handle_notification(event.data)

    def handle_connect(self):
        self._api.authenticate()
        if self._api_init:
            self._api.subscribe()

        if not self._handle_connect:
            self._handle_connect = True
            self._handler.handle_connect()

    def handle_disconnect(self):
        pass
