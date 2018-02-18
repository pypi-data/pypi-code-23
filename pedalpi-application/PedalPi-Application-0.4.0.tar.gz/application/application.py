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

import atexit
import logging
import os
import sys
from pathlib import Path
from shutil import copytree
from unittest.mock import MagicMock

from application.component.components_observer import ComponentsObserver
from application.component.current_pedalboard_observer import CurrentPedalboardObserver
from application.controller.component_data_controller import ComponentDataController
from application.controller.current_controller import CurrentController
from application.controller.device_controller import DeviceController
from application.controller.plugins_controller import PluginsController
from pluginsmanager.observer.autosaver.autosaver import Autosaver
from pluginsmanager.observer.mod_host.mod_host import ModHost

logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', stream=sys.stdout, level=logging.DEBUG)


class Application(object):
    """
    PedalPi - Application is a api for manager the PedalPi - `Components`_
    offers an auto initialization and an updates notification between the components.

    .. _Components: https://github.com/PedalPi/Components

    By a application instance, it's possible obtains a :class:Controller
    for control::

        >>> from application.application import Application
        >>> from application.controller.current_controller import CurrentController

        >>> application = Application()
        >>> current_controller = application.controller(CurrentController)

        >>> print(current_controller.pedalboard)
        <Pedalboard object as Shows with 2 effects at 0x7fa3bcb49be0>

        >>> current_controller.to_next_pedalboard()
        >>> current_controller.pedalboard
        <Pedalboard object as Shows 2 with 1 effects at 0x7fa3bbcdecf8>

    For more details see the Controllers extended classes.

    :param string path_data: Path where the data will be persisted
    :param string address: `mod-host`_ address
    :param bool test: If ``test == True``, the connection with mod-host will be simulated

    .. _mod-host: https://github.com/moddevices/mod-host
    """

    def __init__(self, path_data="data/", address="localhost", test=False):
        self.mod_host = self._initialize(address, test)

        # Data
        path_data = Path(path_data)
        self.path_data = self._initialize_data(path_data)
        self.autosaver = Autosaver(str(path_data / Path('banks')))
        self.manager = self.autosaver.load(DeviceController.sys_effect)

        # Controllers
        self.components = []
        self.controllers = self._load_controllers()

        self._configure_controllers(self.controllers)

        # Observers
        self.components_observer = ComponentsObserver(self.manager)
        current_pedalboard_observer = CurrentPedalboardObserver(self.controller(CurrentController))

        self.manager.register(self.components_observer)
        self.manager.register(current_pedalboard_observer)

    def _initialize(self, address, test=False):
        mod_host = ModHost(address)
        if test:
            mod_host.host = MagicMock()
        else:
            mod_host.connect()

        return mod_host

    def _initialize_data(self, path):
        str_path = str(path)
        if not os.path.exists(str_path):
            default_path_data = os.path.dirname(os.path.abspath(__file__)) / Path('data')

            ignore_files = lambda d, files: [f for f in files if (Path(d) / Path(f)).is_file() and f.endswith('.py')]
            copytree(str(default_path_data), str(os.path.abspath(str_path)), ignore=ignore_files)

            self.log('Data - Create initial data')

        self.log('Data - Loads {}', os.path.abspath(str_path))
        return path

    def _load_controllers(self):
        controllers = {}

        list_controllers = [
            ComponentDataController,
            CurrentController,
            DeviceController,
            PluginsController,
        ]

        for controller in list_controllers:
            controllers[controller.__name__] = controller(self)

        return controllers

    def _configure_controllers(self, controllers):
        for controller in list(controllers.values()):
            controller.configure()
            self.log('Load controller - {}', controller.__class__.__name__)

    def register(self, component):
        """
        Register a :class:`.Component` extended class into Application.
        The components will be loaded when application is loaded (after `start` method is called).

        :param Component component: A module to be loaded when the Application is loaded
        """
        self.components.append(component)

    def register_observer(self, observer):
        """
        Register a :class:`.ApplicationObserver` specialization into Application.
        The observer will receive calls when changes occurs in system, like
        banks creation, current pedalboard changes.

        :param ApplicationObserver observer: The observer who will receive the changes notifications
        """
        self.components_observer.register(observer)

    def unregister_observer(self, observer):
        """
        Unregister an observer in :class:`.Application`.
        The observer not will be more notified of the changes requested in the application API.

        :param ApplicationObserver observer: The observer who will not receive further changes notification
        """
        self.components_observer.unregister(observer)

    def start(self):
        """
        Start the application, initializing your components.
        """
        current_pedalboard = self.controller(CurrentController).pedalboard
        if current_pedalboard is None:
            self.log('Not exists any current pedalboard.')
            self.log('Use CurrentController to set the current pedalboard')
        else:
            self.log('Load current pedalboard - "{}"', current_pedalboard.name)

        self.mod_host.pedalboard = current_pedalboard

        for component in self.components:
            component.init()
            self.log('Load component - {}', component.__class__.__name__)

        self.log('Components loaded')
        atexit.register(self.stop)

    def stop(self):
        """
        Stop the application, closing your components.
        """
        for component in self.components:
            component.close()
            self.log('Stopping component - {}', component.__class__.__name__)

        for controller in self.controllers.values():
            controller.close()
            self.log('Stopping controller - {}', controller.__class__.__name__)

        atexit.unregister(self.stop)

    def controller(self, controller):
        """
        Returns the controller instance by Controller class identifier

        :param Controller controller: Class identifier
        :return: Controller instance
        """
        return self.controllers[controller.__name__]

    def dao(self, dao):
        """
        Returns a Dao persister instance by Dao class identifier

        :param dao: Class identifier
        :return: Dao instance
        """
        return dao(self.path_data)

    def log(self, message, *args, **kwargs):
        logging.info(message.format(*args, **kwargs))
