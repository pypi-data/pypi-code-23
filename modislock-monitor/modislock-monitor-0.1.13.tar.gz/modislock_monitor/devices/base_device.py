# encoding: utf-8

from abc import ABCMeta, abstractmethod


class SensorDict(dict):
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)


class BaseDevice(metaclass=ABCMeta):
    """Base for all devices

    """

    STATE_ACTIVE = 'ACTIVE'
    STATE_INACTIVE = 'INACTIVE'

    def __init__(self, device, callback=None):
        """

        :param device: Port or Pin of the device
        :param callback: Callback on any update to status
        """
        self.__id = None
        self.__pin = device.pin_num
        self.__name = device.name
        self.__current_state = self.STATE_INACTIVE
        self.__callback = callback if callback is not None else self._callback

    def _callback(self, sensor_id, state):
        pass

    @abstractmethod
    def update_state(self, pin, state=None):
        raise NotImplementedError("Update state needs to be implemented")

    @property
    def callback(self):
        return self.__callback

    @property
    def pin(self):
        return self.__pin

    @property
    def name(self):
        return self.__name

    @property
    def device_id(self):
        return self.__id

    @device_id.setter
    def device_id(self, id):
        self.__id = id

    @property
    def current_state(self):
        return self.__current_state

    @current_state.setter
    def current_state(self, state):
        self.__current_state = state

    @abstractmethod
    def deinitialize(self):
        raise NotImplementedError('please implement functionality in deinitialize')

