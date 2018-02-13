import nots.converters as nots_converters
from nots.exceptions import MissingConvertorError


class Serializer:
    def __init__(self):
        self._serializers = nots_converters.DEFAULT_SERIALIZERS.copy()

    def _find_serializer(self, desired_type):
        for serializer in self._serializers:
            if serializer.can_convert(desired_type):
                return serializer

        raise MissingConvertorError(desired_type)

    def serialize(self, obj, desired_type=None):
        if not desired_type:
            desired_type = type(obj)

        serializer = self._find_serializer(desired_type)

        return serializer.convert_from(obj, desired_type, self)

    def deserialize(self, obj, desired_type):
        if desired_type is None:
            raise ValueError

        serializer = self._find_serializer(desired_type)

        return serializer.convert_to(obj, desired_type, self)
