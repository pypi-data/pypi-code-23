from marshmallow.fields import *
from .object_id import ObjectId
from umongo.marshmallow_bonus import GenericReference as umGR, Reference

from datetime import datetime, date
import dateutil.parser
from marshmallow import utils


class GenericReference(umGR):
    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        if self.mongo_world:
            # In mongo world, value a dict of cls and id
            return {'id': str(value['_id']), 'cls': value['_cls']}
        else:
            if isinstance(value, dict):
                return {'id': str(value['id']), 'cls': value['cls']}
            # In OO world, value is a :class:`umongo.data_object.Reference`
            return {'id': str(value.pk), 'cls': value.document_cls.__name__}


class DateTime(DateTime):
    def _serialize(self, value, attr, obj):
        if not value:  # Falsy values, e.g. '', None, [] now valid
            return None
        if isinstance(value, str):
            value = dateutil.parser.parse(value)
        return super()._serialize(value, attr, obj)

    def _deserialize(self, value, attr, data):
        if not value:  # Falsy values, e.g. '', None, [] now valid
            return None
        return super()._deserialize(value, attr, data)


class Method(Method):
    def _deserialize(self, value, attr, data):
        if self.deserialize_method_name:
            try:
                method = utils.callable_or_raise(
                    getattr(self.parent, self.deserialize_method_name, None)
                )
                return method(attr, data)
            except AttributeError:
                pass
        return value
