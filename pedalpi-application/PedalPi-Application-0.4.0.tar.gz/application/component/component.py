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


class Component(metaclass=ABCMeta):

    def __init__(self, application):
        self.application = application

    @abstractmethod
    def init(self):
        """
        Initialize this component
        """
        pass

    def close(self):
        """
        Method called when the application is requested to quit.
        Classes components must implement to safely finish their
        activities.
        """
        pass

    def controller(self, controller):
        return self.application.controller(controller)

    def register_observer(self, observer):
        """
        Calls :meth:`.Application.register_observer`.

        :param ApplicationObserver observer: The observer who will receive the changes notifications
        """
        self.application.register_observer(observer)

    def unregister_observer(self, observer):
        """
        Calls :meth:`.Application.unregister_observer`.

        :param ApplicationObserver observer: The observer who will not receive further changes notification
        """
        self.application.unregister_observer(observer)
