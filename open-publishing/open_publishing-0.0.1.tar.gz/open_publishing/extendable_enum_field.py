from open_publishing.core import SimpleField
from open_publishing.core.enums import ExtendableEnum, FieldKind

class ExtendableEnumField(SimpleField):
    def __init__(self,
                 database_object,
                 aspect,
                 field_locator,
                 dtype,
                 kind = FieldKind.regular,
                 nullable = False,
                 serialized_null = None):
        if not isinstance(dtype, ExtendableEnum):
            raise TypeError('dtype should be instance of ExtendableEnum, got {0}'.format(dtype))
        super(ExtendableEnumField, self).__init__(database_object=database_object,
                                                  aspect=aspect,
                                                  field_locator=field_locator,
                                                  dtype=dtype,
                                                  kind=kind,
                                                  nullable=nullable,
                                                  serialized_null=serialized_null)
        self._internal_id = None

    def _parse_value(self,
                     value):
        if value == self._serialized_null and self._nullable:
            return None
        else:
            ids = self.database_object.context.gjp.resolve_enum(self._dtype, internal_id=value)
            self._internal_id = ids.internal_id
            return ids.enum

    def _value_validation(self,
                          value):
        if value is None and self._nullable:
            return None
        elif value in self._dtype:
            ids = self.database_object.context.gjp.resolve_enum(self._dtype, enum=value)
            self._internal_id = ids.internal_id
            return ids.enum
        else:
            ids = self.database_object.context.gjp.resolve_enum(self._dtype, code=value)
            self._internal_id = ids.internal_id
            return ids.enum

    def _serialize_value(self,
                         value):
        if value is None and self._nullable:
            return self._serialized_null
        else:
            return self._internal_id
        
        
        
