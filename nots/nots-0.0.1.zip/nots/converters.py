import copy
from typing import Dict, List, Union

from nots.exceptions import ConvertError

_MAPPING_FIELD_NAME = '_nots_mapping'


def mapping(**kwargs):
    def wrapper(namedtuple_type):
        setattr(namedtuple_type, _MAPPING_FIELD_NAME, kwargs)
        return namedtuple_type

    return wrapper


def issubclass_safe(cls, classinfo):
    """
    issubclass raises exception with issubclass(typing.Union, typing.Generic), which is bit weird.

    This is a "safer" variant.
    """
    try:
        return issubclass(cls, classinfo)
    except TypeError:
        return False


def get_generic_args(generic):
    return getattr(generic, '__args__')


def _get_typing_type_or_origin(t):
    origin = getattr(t, '__origin__', None)
    if origin is None:
        return t
    return origin


def _is_named_tuple(o) -> bool:
    """
    The best effort to asses that something is NamedTuple with some annotations.
    """
    if issubclass_safe(o, tuple) and o != tuple and hasattr(o, '__annotations__'):
        return True
    return False


Undefined = object()


class BaseConverter:
    def can_convert(self, obj_type):
        raise NotImplementedError

    def convert_to(self, value, desired_type, serializer):
        raise NotImplementedError

    def convert_from(self, value, desired_type, serializer):
        raise NotImplementedError


class SimpleConverter(BaseConverter):
    def __init__(self, types):
        self._types = set(types)

    def _convert(self, value, desired_type):
        if not isinstance(value, desired_type):
            raise ConvertError

        return value

    def can_convert(self, obj_type):
        return obj_type in self._types

    def convert_to(self, value, desired_type, serializer):
        return self._convert(value, desired_type)

    def convert_from(self, value, desired_type, serializer):
        return self._convert(value, desired_type)


class FloatConverter(BaseConverter):
    """
    Float is bit special, because it can accept both int and float.
    """
    def _convert(self, value):
        if not isinstance(value, (int, float)):
            raise ConvertError

        return float(value)

    def can_convert(self, obj_type):
        return obj_type is float

    def convert_to(self, value, desired_type, serializer):
        return self._convert(value)

    def convert_from(self, value, desired_type, serializer):
        return self._convert(value)


class NamedTupleConverter(BaseConverter):
    def can_convert(self, obj_type):
        return _is_named_tuple(obj_type)

    def convert_from(self, obj, desired_type, serializer):
        annotations = getattr(desired_type, '__annotations__')
        mapping = getattr(desired_type, _MAPPING_FIELD_NAME, {})

        return {
            mapping.get(key, key): serializer.serialize(getattr(obj, key), expected_type, )
            for key, expected_type in annotations.items()
        }

    def convert_to(self, d, desired_type, serializer):
        if not isinstance(d, dict):
            raise ConvertError

        annotations: dict = getattr(desired_type, '__annotations__', {})
        mapping: dict = getattr(desired_type, _MAPPING_FIELD_NAME, {})

        def get_field(key):
            mapped_key = mapping.get(key, key)
            return d.get(mapped_key, None)

        kwargs = {
            key: serializer.deserialize(get_field(key), expected_type, )
            for key, expected_type in annotations.items()
        }

        return desired_type(**kwargs)


class UnionConverter(BaseConverter):
    def can_convert(self, obj_type):
        if not getattr(obj_type, '__origin__', None) is Union:
            return False

        generic_args = get_generic_args(obj_type)
        return len(generic_args) == 2 and type(None) in generic_args

    def _get_non_none(self, desired_type):
        a, b = get_generic_args(desired_type)

        return a if b is type(None) else b

    def convert_to(self, value, desired_type, serializer):
        if value is None:
            return None

        non_none = self._get_non_none(desired_type)
        return serializer.serialize(value, non_none)

    def convert_from(self, value, desired_type, serializer):
        if value is None:
            return None

        non_none = self._get_non_none(desired_type)
        return serializer.deserialize(value, non_none)


class ListConverter(BaseConverter):
    def _retrieve_value_type(self, desired_type):
        if issubclass(desired_type, List):
            desired_type_args = desired_type.__args__
            if desired_type_args:
                return desired_type_args[0]

        if issubclass(desired_type, list):
            return None

        raise ConvertError

    def convert_to(self, value, desired_type, serializer):
        value_type = self._retrieve_value_type(desired_type)
        if value_type:
            return [
                serializer.deserialize(item, value_type) for item in value
            ]

        return [
            copy.deepcopy(item) for item in value
        ]

    def convert_from(self, value, desired_type, serializer):
        return [serializer.serialize(item) for item in value]

    def can_convert(self, obj_type):
        return issubclass_safe(obj_type, list)


class DictConverter(BaseConverter):
    def can_convert(self, obj_type):
        t = _get_typing_type_or_origin(obj_type)

        if not issubclass_safe(t, Dict):
            return False

        args = get_generic_args(obj_type)

        if not args:
            return False

        if issubclass_safe(args[0], str):
            return True

    def convert_to(self, value: dict, desired_type, serializer):
        if not isinstance(value, dict):
            raise ConvertError

        args = get_generic_args(desired_type)
        t = args[1]

        return {
            key: serializer.deserialize(value, t, ) for key, value in value.items()
        }

    def convert_from(self, value, desired_type, serializer):
        if not isinstance(value, dict):
            raise ConvertError

        args = get_generic_args(desired_type)
        t = args[1]

        return {
            key: serializer.serialize(value, t) for key, value in value.items()
        }


DEFAULT_SERIALIZERS = [
    SimpleConverter((int, bool, type(None), str)),
    FloatConverter(),
    ListConverter(),
    NamedTupleConverter(),
    UnionConverter(),
    DictConverter()
]