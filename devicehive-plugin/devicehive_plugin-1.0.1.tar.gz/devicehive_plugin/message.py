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


import json
import uuid

from devicehive_plugin.error import ResponseMessageError


__all__ = ['RequestMessage', 'ResponseMessage']


class BaseMessage(object):

    ID_KEY = 'id'
    TYPE_KEY = 't'
    ACTION_KEY = 'a'
    PAYLOAD_KEY = 'p'
    STATUS_KEY = 's'

    # actions
    AUTHENTICATE_ACTION = 'authenticate'
    SUBSCRIBE_ACTION = 'subscribe'
    UNSUBSCRIBE_ACTION = 'unsubscribe'

    # types
    PLUGIN_TYPE = 'plugin'
    TOPIC_TYPE = 'topic'
    NOTIFICATION_TYPE = 'notif'

    SUCCESS_VALUE = 0

    def __init__(self, id_, type_, action, payload=None, status=None):
        self._id = id_
        self._type = type_
        self._action = action
        self._payload = payload if payload is not None else {}
        self._status = status

    @property
    def is_authenticate(self):
        return self._action == self.AUTHENTICATE_ACTION

    @property
    def is_subscribe(self):
        return self._action == self.SUBSCRIBE_ACTION

    @property
    def is_unsubscribe(self):
        return self._action == self.UNSUBSCRIBE_ACTION

    @property
    def is_plugin_type(self):
        return self._type == self.PLUGIN_TYPE

    @property
    def is_topic_type(self):
        return self._type == self.TOPIC_TYPE

    @property
    def is_notification_type(self):
        return self._type == self.NOTIFICATION_TYPE

    @property
    def is_success(self):
        return self._status == self.SUCCESS_VALUE

    @property
    def id(self):
        return self._id

    @property
    def action(self):
        return self._action

    @property
    def status(self):
        return self._status

    @property
    def type(self):
        return self._type


class ResponseMessage(BaseMessage):

    PAYLOAD_MESSAGE_KEY = 'm'

    def __init__(self, message):
        message = json.loads(message)
        id_ = message.get(self.ID_KEY)
        type_ = message[self.TYPE_KEY]
        action = message.get(self.ACTION_KEY)
        payload = message.get(self.PAYLOAD_KEY)
        status = message[self.STATUS_KEY]

        super(ResponseMessage, self).__init__(id_, type_, action, payload,
                                              status)

        self._payload_message = self._payload.get(self.PAYLOAD_MESSAGE_KEY)

    @property
    def payload_message(self):
        return self._payload_message


class RequestMessage(BaseMessage):

    def __init__(self, api, type_, action, payload=None):
        self._api = api
        id_ = str(uuid.uuid4())
        super(RequestMessage, self).__init__(id_, type_, action, payload)

    def encode(self):
        message = {
            self.ID_KEY: self._id,
            self.TYPE_KEY: self._type,
            self.ACTION_KEY: self._action,
            self.PAYLOAD_KEY: self._payload,
        }
        return json.dumps(message)

    def set_payload(self, key, value):
        self._payload[key] = value

    def execute(self):
        response = self._api.transport.request(self)

        if response.is_success:
            return response
        raise ResponseMessageError(response.payload_message)
