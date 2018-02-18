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

from abc import ABCMeta, abstractmethod
from pluginsmanager.observer.updates_observer import UpdatesObserver


class ApplicationObserver(UpdatesObserver, metaclass=ABCMeta):
    """
    The :class:`.ApplicationObserver` extends :class:`.UpdatesObserver`.
    It is an abstract class definition for treatment of changes in some class model.
    Your methods are called when occurs any change in Bank, Pedalboard, Effect, etc.

    To do this, it is necessary that the :class:`.ApplicationObserver` objects
    be registered in application (using :meth:`.Application.register_observer`
    or :meth:`.Component.register_observer`), so that it reports the changes.
    """

    @abstractmethod
    def on_current_pedalboard_changed(self, pedalboard, **kwargs):
        """
        Called when the current pedalboard is changed

        :param Pedalboard pedalboard: New current pedalboard
        """
        pass
