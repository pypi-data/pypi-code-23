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

from application.component.application_observer import ApplicationObserver
from pluginsmanager.observer.update_type import UpdateType


class CurrentPedalboardObserver(ApplicationObserver):
    """
    This viewer allows change the current pedalboard
    if it is updated or removed or if your bank is updated or removed.
    """

    def __init__(self, current_controller):
        """
        :param CurrentController current_controller:
        """
        super(CurrentPedalboardObserver, self).__init__()
        self._current_controller = current_controller

    def on_bank_updated(self, bank, update_type, index, origin, **kwargs):
        if update_type == UpdateType.UPDATED:
            old_bank = kwargs['old']
            if old_bank == self._current_controller.bank:
                self._current_controller.set_bank(bank, try_preserve_index=True)

        elif update_type == UpdateType.DELETED:
            if bank == self._current_controller.bank:
                next_bank_index = self._current_controller.next_bank_index(index-1)
                new_current_bank = origin.banks[next_bank_index]

                self._current_controller.set_bank(new_current_bank)

    def on_pedalboard_updated(self, pedalboard, update_type, index, origin, **kwargs):
        if update_type == UpdateType.UPDATED:
            old_pedalboard = kwargs['old']

            if pedalboard == self._current_controller.pedalboard \
            or old_pedalboard == self._current_controller.pedalboard:
                self._current_controller.set_pedalboard(pedalboard, notify=False, force=True)

    def on_effect_status_toggled(self, effect, **kwargs):
        pass

    def on_connection_updated(self, connection, update_type, pedalboard, **kwargs):
        pass

    def on_param_value_changed(self, param, **kwargs):
        pass

    def on_effect_updated(self, effect, update_type, index, origin, **kwargs):
        pass

    def on_current_pedalboard_changed(self, pedalboard, **kwargs):
        pass
