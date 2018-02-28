# -*- coding: utf-8 -*-
"""Defines handler for identifiers"""

import wx



class Identifiers(object):
    """Application identifiers handler"""
    _identifiers = {}

    def __init__(self):
        """Ensures this is a singleton"""
        raise RuntimeError('IdentifiersHandler is a singleton')
        super(IdentifiersHandler, self).__init__()

    @classmethod
    def new(cls, name=None, value=None):
        """Create a new identifier"""
        if name:
            if name in cls._identifiers:
                raise RuntimeError('Identifier {name} already exists'.format(name=name))
            if value is None:                 
                value = wx.Window.NewControlId()
                while value in cls._identifiers.values():
                    value = wx.Window.NewControlId()
            else:
                assert value not in cls._identifiers.values()
            cls._identifiers[name] = value
            return value
        else:
            return wx.Window.NewControlId()

    @classmethod
    def register(cls, name, value=None):
        """Register a identifier"""
        local_value = cls._identifiers.get(name, None)
        if local_value is None:
            local_value = cls.new(name, value)
        elif value is not None:
            assert value == local_value
        return local_value
