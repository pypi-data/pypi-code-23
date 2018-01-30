# -*- coding: utf8 -*-
"""
Compatibility library (Python Compat 2-3) used to write
one general code both for Python 2.x and 3.x
"""

import sys


py_version = 0


def metaclass(metacls):
    """ Compatible both with P2 and P3 metaclass usage """
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metacls(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


def str_decode(value):
    return value.decode('utf-8') if py_version == 2 else str(value)


def strlen(value):
    return len(value) if py_version == 3 else len(value.decode('utf-8'))


if sys.version_info[0] == 2:
    py_version = 2
    xrange = xrange

else:
    py_version = 3
    xrange = range

