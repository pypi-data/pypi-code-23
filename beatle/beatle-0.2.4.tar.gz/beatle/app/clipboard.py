# -*- coding: utf-8 -*-

# This file defines a ver basic private clipboard
# whose mission is to handle data and provide info about

import uuid
from beatle.lib.decorators import classproperty


class clipboard(object):
    "Basic clipboard definition"
    # propiedades
    __registered__classes = {}
    __current_data = None

    def __init__(self):
        """Initialization. Setup handlers"""
        super(clipboard, self).__init__()

    @classproperty
    def is_empty(self):
        """has data?"""
        return not self.__current_data

    @classmethod
    def register(cls, _type):
        """register a new class or access it"""
        if _type not in cls.__registered__classes:
            cls.__registered__classes[_type] = uuid.uuid4()
        return cls.__registered__classes[_type]

    @classmethod
    def copy(cls, data):
        """copy data to clipboard"""
        assert type(data) in cls.__registered__classes
        if id(data) != id(cls.__current_data):
            cls.__current_data = data

    @classproperty
    def info(self):
        """return clipboard info"""
        return self.__current_data and self.__registered__classes[
            type(self.__current_data)]

    @classproperty
    def data(self):
        """return the current data"""
        return self.__current_data

