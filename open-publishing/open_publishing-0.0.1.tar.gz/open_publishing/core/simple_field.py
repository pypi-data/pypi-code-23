import datetime
import time

from .enums import ValueStatus, FieldKind, Enum, ExtendableEnum
from .field import Field


class SimpleField(Field):
    def __init__(self,
                 database_object,
                 aspect,
                 field_locator,
                 dtype = None,
                 kind = FieldKind.regular,
                 nullable = False,
                 serialized_null = None):

        if kind not in [FieldKind.regular, FieldKind.readonly]:
            raise ValueError("expected FieldKind.regular or FieldKind.readonly, got {0}".format(kind))

        super(SimpleField, self).__init__(database_object,
                                          aspect,
                                          kind)
        self._field_locator = field_locator
        self._dtype = dtype
        self._nullable = nullable
        self._serialized_null = serialized_null
        self._value = None

    @property
    def value(self):
        if self._status is ValueStatus.none:
            raise RuntimeError("Accessing to field which is not set")
        else :
            return self._value

    def hard_set(self,
                 value):
        self._value = self._value_validation(value)
        self._status = ValueStatus.hard

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard :
            value = self._master_object(gjp)
            for fname in self._field_locator.split("."):
                if fname in value:
                    value = value[fname]
                else :
                    return
            self._value = self._parse_value(value)
            self._status = ValueStatus.soft

    def gjp(self,
            gjp):
        if self._status is ValueStatus.hard:
            cursor = gjp
            for fname in self._field_locator.split(".")[:-1]:
                if fname not in cursor:
                    cursor[fname] = {}
                cursor = cursor[fname]
            cursor[self._field_locator.split(".")[-1]] = self._serialize_value(self._value)

    def _serialize_value(self,
                         value):
        if value is None and self._nullable:
            return self._serialized_null
        elif self._dtype is bool:
            return value
        elif self._dtype in [datetime.date, datetime.datetime]:
            return int(time.mktime(value.timetuple()))
        elif isinstance(self._dtype, ExtendableEnum):
            return value.identifier
        elif isinstance(self._dtype, Enum):
            return value.identifier
        else:
            return value
    
    def _parse_value(self,
                     value):
        if value == self._serialized_null and self._nullable:
            return None
        elif self._dtype in (int, float) :
            return self._dtype(value)
        elif self._dtype is bool and isinstance(value, bool):
            return value
        elif self._dtype is str and isinstance(value, str):
            return value
        elif self._dtype is str and isinstance(value, str):
            return str(value)
        elif self._dtype is str and isinstance(value, str):
            return value
        elif self._dtype is str and isinstance(value, str):
            return str(value)
        elif self._dtype is datetime.datetime and isinstance(value, int):
            return datetime.datetime.fromtimestamp(value)
        elif self._dtype is datetime.date and isinstance(value, int):
            return datetime.date.fromtimestamp(value)
        elif isinstance(self._dtype, ExtendableEnum):
            return self._dtype.extend(value)
        elif isinstance(self._dtype, Enum):
            return self._dtype.from_id(value)
        elif self._dtype is set:
            return set(value)
        else :
            raise RuntimeError("Unable to set from json, field locator '{0}'".format(self._field_locator))
        
    def _value_validation(self,
                          value):
        if value is None and self._nullable:
            return value
        elif isinstance(value, str) and self._dtype is str:
            return str(value)
        elif isinstance(self._dtype, (Enum, ExtendableEnum)):
            if value in self._dtype:
                return value
            else:
                raise ValueError("Unexepected enum value {0}".format(value))
        elif isinstance(value, self._dtype):
            return value
        else:
            raise TypeError("expected instance of {0}, got instance of {1}".format(self._dtype,
                                                                                    type(value)))


