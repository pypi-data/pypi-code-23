from nots.serializer import Serializer
from nots.converters import mapping


_serializer = Serializer()


def serialize(obj, desired_type=None):
    _serializer.serialize(obj, desired_type)


def deserialize(obj, desired_type):
    _serializer.deserialize(obj, desired_type)
