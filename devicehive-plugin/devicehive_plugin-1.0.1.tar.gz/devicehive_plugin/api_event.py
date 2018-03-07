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

from devicehive_plugin.command import Command
from devicehive_plugin.notification import Notification

__all__ = ['ApiEvent']


class ApiEvent(object):

    DATA_KEY = 'b'
    ACTION_KEY = 'a'
    COMMAND_KEY = 'command'
    NOTIFICATION_KEY = 'notification'

    SERVER_COMMAND_INSERT_ACTION = 21
    SERVER_COMMAND_UPDATE_ACTION = 23
    SERVER_NOTIFICATION_ACTION = 10

    COMMAND_INSERT_ACTION = 'command/insert'
    COMMAND_UPDATE_ACTION = 'command/update'
    NOTIFICATION_ACTION = 'notification/insert'

    ACTION_MAP = {
        SERVER_COMMAND_INSERT_ACTION: COMMAND_INSERT_ACTION,
        SERVER_COMMAND_UPDATE_ACTION: COMMAND_UPDATE_ACTION,
        SERVER_NOTIFICATION_ACTION: NOTIFICATION_ACTION
    }

    def __init__(self, event):
        self._raw_data = json.loads(event)[self.DATA_KEY]
        self._action = self.ACTION_MAP[self._raw_data[self.ACTION_KEY]]
        self._data = None

        if self.is_command_event:
            self._data = Command(self._raw_data[self.COMMAND_KEY])
        elif self.is_notification_event:
            self._data = Notification(self._raw_data[self.NOTIFICATION_KEY])

    @property
    def is_command_insert_event(self):
        return self._action == self.COMMAND_INSERT_ACTION

    @property
    def is_command_update_event(self):
        return self._action == self.COMMAND_UPDATE_ACTION

    @property
    def is_command_event(self):
        return self.is_command_insert_event or self.is_command_update_event

    @property
    def is_notification_event(self):
        return self._action == self.NOTIFICATION_ACTION

    @property
    def action(self):
        return self._action

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def data(self):
        return self._data
