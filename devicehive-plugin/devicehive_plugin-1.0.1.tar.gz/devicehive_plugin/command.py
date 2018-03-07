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


class Command(object):

    DEVICE_ID_KEY = 'deviceId'
    ID_KEY = 'id'
    USER_ID_KEY = 'userId'
    COMMAND_KEY = 'command'
    PARAMETERS_KEY = 'parameters'
    LIFETIME_KEY = 'lifetime'
    TIMESTAMP_KEY = 'timestamp'
    LAST_UPDATED_KEY = 'lastUpdated'
    STATUS_KEY = 'status'
    RESULT_KEY = 'result'

    def __init__(self, command):
        self._device_id = command[self.DEVICE_ID_KEY]
        self._id = command[self.ID_KEY]
        self._user_id = command[self.USER_ID_KEY]
        self._command = command[self.COMMAND_KEY]
        self._parameters = command[self.PARAMETERS_KEY]
        self._lifetime = command[self.LIFETIME_KEY]
        self._timestamp = command[self.TIMESTAMP_KEY]
        self._last_updated = command[self.LAST_UPDATED_KEY]
        self._status = command[self.STATUS_KEY]
        self._result = command[self.RESULT_KEY]

    @property
    def device_id(self):
        return self._device_id

    @property
    def id(self):
        return self._id

    @property
    def user_id(self):
        return self._user_id

    @property
    def command(self):
        return self._command

    @property
    def parameters(self):
        return self._parameters

    @property
    def lifetime(self):
        return self._lifetime

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def last_updated(self):
        return self._last_updated

    @property
    def status(self):
        return self._status

    @property
    def result(self):
        return self._result
