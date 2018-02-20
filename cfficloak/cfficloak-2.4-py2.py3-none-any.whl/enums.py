from __future__ import absolute_import

import six
from .typedef import CType

if six.PY3:
    long = int


class Enum(int if six.PY3 else long):
    """
    This is a base class for wrapping enum ints
    wrapenum() below will subtype it for a particular enum
    and return a wrapped result which will still work as an int
    but display/print as the string representation from the enum
    """
    _names = {}

    def __new__(cls, *args, **kwargs):
        return super(Enum, cls).__new__(cls, *args, **kwargs)

    def __str__(self):
        return self._names.get(int(self), str(int(self)))


# Cache generated enum types
_enumTypes = {}


def wrapenum(retval, enumTypeDescr):
    """
    Wraps enum int in an auto-generated wrapper class. This is used automatically when
    cmethod() returns an enum type
    :param retval: integer
    :param enumTypeDescr or CType: the cTypeDescr for the enum
    :return: subclass of Enum
    """
    def _newEnumType(enumTypeDescr):
        _enumTypes[enumTypeDescr.cname] = type(enumTypeDescr.cname, (Enum, ), {"_names": enumTypeDescr.elements})
        return _enumTypes[enumTypeDescr.cname]
    if isinstance(enumTypeDescr, CType):
        enumTypeDescr = enumTypeDescr.ffi.typeof(enumTypeDescr.typedef)
    enum = _enumTypes.get(enumTypeDescr.cname, _newEnumType(enumTypeDescr))
    return enum(retval)