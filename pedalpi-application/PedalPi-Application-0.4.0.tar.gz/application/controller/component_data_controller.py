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

from application.dao.component_dao import ComponentDao

from application.controller.controller import Controller


class ComponentDataController(Controller):
    """
    Maybe the pedalboard data it's not sufficient for management in a custom
    :class:`Components`. For example, in a possible visual pedalboard manager is
    necessary persist the effects positions.

    :class:`ComponentDataController` offers a way to salve and restore data.

    For your component, create a unique identifier (key) and use it for manage all
    your Component data. For example::

        >>> key = 'raspberry-p0'
        >>> controller = application.controller(ComponentDataController)

        >>> # If key not exists, returns {}
        >>> controller[key]
        {}

        >>> controller[key] = {'pedalboard': 0}
        >>> controller[key]
        {'pedalboard': 0}

        >>> # The new data overrides old data
        >>> controller[key] = {'pedalboards': []}
        >>> controller[key]
        {'pedalboards': []}

        >>> # Changes in returned object will not change the persisted data
        >>> data = controller[key]
        >>> data['component'] = 'Raspberry P0'
        >>> data
        {'pedalboards': [], 'component': 'Raspberry P0'}
        >>> controller[key]
        {'pedalboards': []}

        >>> # Remove all content for 'raspberry-p0'
        >>> del controller[key]
        >>> controller[key]
        {}

    .. warning::
        :class:`ComponentDataController` does not have access control,
        which means that any Component that eventually
        use *ComponentDataController* may interfere with the content
        (accessing, changing or removing).

    .. warning::
        It's a easy way for save simple data. Please, don't save binaries or big content
    """

    dao = None
    __data = None

    def configure(self):
        self.dao = self.app.dao(ComponentDao)
        self.__data = self.dao.load()

    def __getitem__(self, key):
        """
        Returns the data for the informed `key`::

            >>> component_data_controller[key]
            {'any key': 'any data'}

        If no data was saved for this key, an empty dictionary is returned::

            >>> component_data_controller['a crazy key']
            {}

        :param string key:
        :return dict: Content if exist for key informed, else empty `dict`
        """
        try:
            return dict(self.__data[key])
        except KeyError:
            return {}

    def __setitem__(self, key, value):
        """
        Change the `key` identifier content to `value`::

            >>> component_data_controller[key] = {'any key': 'any data'}

        :param string key: Identifier
        :param value: Data will be persisted
        """
        self.__data[key] = value

        self.dao.save(self.__data)

    def __delitem__(self, key):
        """
        Remove all `item` identifier content::

            >>> del component_data_controller[key]

        :param string key: Identifier
        """
        del self.__data[key]

        self.dao.save(self.__data)
