"""A collection of general purpose utility functions and classes that can be 
used within scripts and web applications.

Copyright (c) 2017, Hazeltek Solutions.
"""
## imports
import codecs
import os
import sys
import binascii
from collections import namedtuple
from ._compat import integer_types



## singleton
Missing = type('MissingType', (), {'repr': lambda x: 'Missing'})()

## figure out file system encoding
fs_enc = sys.getfilesystemencoding()
try:
    if codecs.lookup(fs_enc).name == 'ascii':
        fs_enc = 'utf-8'
except LookupError:
    pass


#+============================================================================+
#| util functions
#+============================================================================+
def generate_random_digest(num_bytes=28, urandom=None, to_hex=None):
    """Generates a random hash and returns the hex digest.
    """
    if urandom is None:
        urandom = os.urandom
    if to_hex is None:
        to_hex = binascii.hexlify
    
    rvalues = urandom(num_bytes)
    return to_hex(rvalues)


def to_text(value):
    if isinstance(value, float):
        if int(value) == value:
            value = int(value)
    try:
        value = str(value)
    except UnicodeError:
        value = None
    return value


def to_bool(value):
    if value is not None:
        if value in (True, False, 1, 0):
            return bool(value)

        value = to_text(value)
        if not value:
            return None
        if value.upper() in ('TRUE', 'YES', 'T', 'Y'):
            return True
        elif value.upper() in ('FALSE', 'NO', 'F', 'N'):
            return False
    return None


def to_enum(enum_type, value):
    if value is not None:
        if isinstance(value, integer_types):
            try:
                return enum_type(value)
            except ValueError:
                return None
        value = to_text(value)
        if value and hasattr(enum_type, value):
            return enum_type[value]
    return None


#+============================================================================+
#| base classes
#+============================================================================+
class AttrDict(dict):
    """Represents a dictionary object whose elements can be accessed and set 
    using the dot object notation. Thus in addition to `foo['bar']`, `foo.bar`
    can equally be used.
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
    
    def __getattr__(self, key):
        return self.__getitem__(key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __getitem__(self, key):
        return dict.get(self, key, None)
    
    def __getstate__(self):
        return dict(self)
    
    def __setstate__(self, value):
        dict.__init__(self, value)
    
    def __repr__(self):
        return '<AttrDict %s>' % dict.__repr__(self)
    
    @staticmethod
    def make(obj):
        """Converts all dict-like elements to a storage object.
        """
        if not isinstance(obj, (dict,)):
            raise ValueError('obj must be a dict or dict-like object')

        _make = lambda d: AttrDict({ k: d[k]
            if not isinstance(d[k], (dict, AttrDict))
            else _make(d[k])
                for k in d.keys()
        })
        return _make(obj)


class CoordinatesLite(namedtuple('CoordinatesLite', 'lng lat')):
    """Defines a lite version of a structure which makes it easy storing gps
    coordinates.
    """
    def __new__(cls, lng, lat):
        if lng == None: raise ValueError('lng required')
        if lat == None: raise ValueError('lat required')
        return super(CoordinatesLite, cls).__new__(
            cls, float(lng), float(lat)
        )


class Coordinates(namedtuple('Coordinates', 'lng lat alt error')):
    """Defines a structure which makes it easy storing gps coordinates.
    """
    def __new__(cls, lng, lat, alt=None, error=None):
        if lng == None: raise ValueError('lng required')
        if lat == None: raise ValueError('lat required')
        return super(Coordinates, cls).__new__(
            cls, float(lng), float(lat), 
            float(alt) if alt != None else alt, 
            int(error) if error != None else error
        )
    
    @property
    def lite(self):
        return CoordinatesLite(self.lng, self.lat)


class cached_property(property):
    """A decorator that converts a function into a lazy property. The function
    wrapped is called the first time to retrieve the result and then that
    calculated result is used the next time you access the value.

        class Foo(object):
            @cached_property
            def foo(self):
                return 42

    The class has to have  a `__dict__` in order for this property to work.
    """
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, Missing)
        if value is Missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
