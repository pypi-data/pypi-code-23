from .simple_field import SimpleField
from .database_object import DatabaseObject

class DatabaseObjectField(SimpleField):
    def __init__(self,
                 parent,
                 aspect,
                 field_locator,
                 dtype,
                 nullable = False):
        if not issubclass(dtype, DatabaseObject):
            ValueError('expected derived from DatabaseObject, got: "{0}"'.format(dtype))
        super(DatabaseObjectField, self).__init__(database_object=parent,
                                                  aspect=aspect,
                                                  field_locator=field_locator,
                                                  dtype=dtype,
                                                  nullable=nullable)

    def _parse_value(self,
                     value):
        if value == 0:
            if self._nullable:
                return None
            else:
                raise ValueError('got "0", for not nullable field')
        else:
            return self._dtype(self.database_object.context,
                               value)

    def _value_validation(self,
                          value):
        if value is None and self._nullable:
            return None
        elif isinstance(value, self._dtype):
            return value
        elif isinstance(value, int):
            return self._dtype(self.database_object.context,
                               value)
        elif isinstance(value, str):
            return self._dtype(self._dtype.id_from_guid(value),
                               value)
        else:
            raise TypeError("expected instance of user, user_id, user_guid or None, got instance of {0}".format(type(value)))

    def _serialize_value(self,
                         value):
        if value is None:
            return 0
        else:
            return value._object_id
        
    def flush(self):
        if self._value:
            self._value.flush()
        
