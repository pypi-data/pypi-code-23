# Copyright 2017 SrMouraSilva
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

from application.controller.controller import Controller
from pluginsmanager.model.system.system_effect import SystemEffect


class DeviceController(Controller):
    """
    Apply changes in the device (mod-host)
    """
    sys_effect = SystemEffect('system', ('capture_1', 'capture_2'), ('playback_1', 'playback_2'))

    def __init__(self, application):
        super(DeviceController, self).__init__(application)

    def configure(self):
        self.app.manager.register(self.mod_host)

    def close(self):
        self.mod_host.close()

    @property
    def mod_host(self):
        return self.app.mod_host

    @property
    def pedalboard(self):
        return self.mod_host.pedalboard

    @pedalboard.setter
    def pedalboard(self, pedalboard):
        self.mod_host.pedalboard = pedalboard
