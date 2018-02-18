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


class ComponentsObserver(ApplicationObserver):

    def __init__(self, manager):
        super(ComponentsObserver, self).__init__()
        self.observers = []
        self._manager = manager

    def register(self, observer):
        self.observers.append(observer)
        observer.manager = self.manager

    def unregister(self, observer):
        observer.manager = None
        self.observers.remove(observer)

    @property
    def scope(self):
        return self._manager.observer_manager.scope

    def on_bank_updated(self, bank, update_type, index, origin, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_bank_updated(bank, update_type, index=index, origin=origin, **kwargs)

    def on_pedalboard_updated(self, pedalboard, update_type, index, origin, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_pedalboard_updated(pedalboard, update_type, index=index, origin=origin, **kwargs)

    def on_effect_updated(self, effect, update_type, index, origin, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_effect_updated(effect, update_type, index=index, origin=origin, **kwargs)

    def on_effect_status_toggled(self, effect, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_effect_status_toggled(effect, **kwargs)

    def on_param_value_changed(self, param, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_param_value_changed(param, **kwargs)

    def on_connection_updated(self, connection, update_type, pedalboard, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_connection_updated(connection, update_type, pedalboard=pedalboard, **kwargs)

    def on_current_pedalboard_changed(self, pedalboard, **kwargs):
        for observer in self.observers:
            if observer != self.scope:
                observer.on_current_pedalboard_changed(pedalboard, **kwargs)
