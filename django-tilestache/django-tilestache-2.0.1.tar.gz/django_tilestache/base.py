# coding: utf-8
from uuid import uuid4
from .exceptions import ConfigurationException


class BaseConfiguration(object):

    """
    Base configuration class.
    It supports creation using dictionaries
    that will auto assign values to instance
    members if the keys match.
    keys that do no exist on the instance
    will be discarded.
    Ideally all configurations will
    inherit this class.
    """

    optional_properties = tuple()

    id = None

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            self.id = uuid4()
        for k in kwargs.keys():
            if hasattr(self, k):
                setattr(self, k, kwargs[k])

    def is_valid(self):
        raise NotImplementedError('is_valid must be implemented.')

    def to_dict(self):
        if self.is_valid():
            return self._to_dict()

        raise ConfigurationException('The configuration for this object is not valid')

    def _to_dict(self):
        raise NotImplementedError('_serialize must be implemented.')

    def _merge_properties(self, output):
        for prop in self.optional_properties:
            if isinstance(prop, tuple):
                prop, key = prop[0], prop[1]
            else:
                prop, key = prop, prop
            if hasattr(self, prop):
                prop_value = getattr(self, prop)
                if prop_value:
                    output[key] = prop_value
        return output
