"""Defines core functions an classes.
"""
import os
from collections import namedtuple



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
