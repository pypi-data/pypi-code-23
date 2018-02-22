from marshmallow.exceptions import ValidationError
from marshmallow.fields import Field

import bson


class ObjectId(Field):
    """
    Marshmallow field for :class:`bson.ObjectId`
    """

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return str(value)

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        if not isinstance(value, (bytes, str, ObjectId)):
            raise ValidationError('Invalid ObjectId.')
        try:
            return bson.ObjectId(value)
        except bson.errors.InvalidId:
            raise ValidationError('Invalid ObjectId.')