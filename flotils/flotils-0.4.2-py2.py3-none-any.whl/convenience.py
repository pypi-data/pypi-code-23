# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2018, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2018-01-27"
# Created: 2018-01-27 10:44

import abc


def format_vars(instance):
    attrs = vars(instance)
    return ", ".join("{}={}".format(key, value) for key, value in attrs.items())


class FromToDictBase(object):
    """ Class allowing automatic loading to and from dicts of attributes """
    __metaclass__ = abc.ABCMeta

    @classmethod
    def from_dict(cls, d):
        new = cls()
        if not d:
            return new
        attrs = vars(new)
        for key in d:
            if key in attrs:
                # both in dict and this class
                setattr(new, key, d[key])
        return new

    def to_dict(self):
        attrs = vars(self)
        res = {}
        for key, value in attrs.items():
            if isinstance(value, FromToDictBase):
                res[key] = value.to_dict()
            else:
                res[key] = value
        return res

    def clone(self):
        return self.from_dict(self.to_dict())


class PrintableBase(object):
    """ Class with auto readable values """
    __metaclass__ = abc.ABCMeta

    def __str__(self):
        return "<{}>({})".format(self.__class__.__name__, format_vars(self))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
