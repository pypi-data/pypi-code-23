# coding: utf-8
from rest_framework import serializers


class PolySerializer(object):

    """
    Simple instance that holds
    a few informations about
    who is the best serializer for this
    data
    """

    serializer_class = None
    can_serialize = None
    can_deserialize = None

    def __init__(self,
                 serializer_class=None,
                 can_serialize=None,
                 can_deserialize=None):

        if not serializer_class:
            raise ValueError('serializer_class cannot be null')
        if not can_serialize:
            raise ValueError('valid_obj cannot be null')
        if not can_deserialize:
            raise ValueError('valid_data cannot be null')

        self.serializer_class = serializer_class
        self.can_serialize = can_serialize
        self.can_deserialize = can_deserialize

    def can_serialize(self, data, context):
        """
        returns true if this object can be
        serialized with this serializer
        """
        if self.can_serialize:
            return self.can_serialize(data, context)

        return False

    def can_deserialize(self, data, context):
        """
        returns true if this object can be
        deserialized with this serializer
        """
        if self.can_deserialize:
            return self.can_deserialize(data, context)
        return False


class PolymorficSerializer(serializers.Serializer):

    """
    PolymorficSerializer can define
    a iterable of poly_serializers.
    They will be used to determine
    which serializer is suited to
    do the work on a particular object

    This itetable must hold instances
    of PolySerializer
    """

    poly_serializers = None

    def validate_poly_serializer(self):

        if not self.poly_serializers:
            raise ValueError('poly_serializers should not be null. it should be a iterable')

        return True

    def is_valid(self, raise_exception=False):
        self.validate_poly_serializer()

        suited = [p for p in self.poly_serializers if p.can_deserialize(data=self.initial_data, context=self.context)]
        if len(suited) <= 0:
            raise ValueError('no serializers are suitable')

        poly_serializer = suited.pop(0).serializer_class(data=self.initial_data, context=self.context)
        return poly_serializer.is_valid(raise_exception)

    def to_representation(self, obj):

        self.validate_poly_serializer()
        suited_serializers = [p for p in self.poly_serializers if p.can_serialize(obj, context=self.context)]
        if len(suited_serializers) <= 0:
            raise ValueError('no serializers are suitable for this object')
        poly_serializer = suited_serializers.pop(0).serializer_class(data=obj, context=self.context)
        return poly_serializer.to_representation(obj)

    def to_internal_value(self, data):

        self.validate_poly_serializer()

        suited = [p for p in self.poly_serializers if p.can_deserialize(data, context=self.context)]
        if len(suited) <= 0:
            raise ValueError('no serializers are suitable for this data')
        poly_serializer = suited.pop(0).serializer_class(data=data, context=self.context)
        return poly_serializer.to_internal_value(data)
