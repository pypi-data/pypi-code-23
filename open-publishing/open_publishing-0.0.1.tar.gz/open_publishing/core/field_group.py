import traceback

from .enums import ValueStatus, FieldKind
from .field import Field
from .field_descriptor import FieldDescriptor


class FieldGroup(Field):
    def __init__(self,
                 database_object):
        super(FieldGroup, self).__init__(database_object=database_object,
                                         kind=FieldKind.regular)
        self._status = ValueStatus.soft
        self._fields = {}

    @property
    def value(self):
        return self

    def hard_set(self,
                 value):
        if not isinstance(value, self.__class__):
            raise ValueError("Expected instance of {0}".format(self.__class__))
        for name, field in list(value._fields.items()):
            if field.status is not ValueStatus.default:
                fd = FieldDescriptor(name)
                fd.__set__(self, fd.__get__(value, name))
            
    def invalidate(self):
        for field in list(self._fields.values()):
            field.flush()
            field.invalidate()

    def update(self,
               gjp):
        for name, field in list(self._fields.items()):
            try:
                field.update(gjp)
            except Exception as e:
                raise RuntimeError("Update failed for field: '{0}'\n{1}".format(name,
                                                                                ''.join(traceback.format_exception_only(type(e), e))))

    def gjp(self,
            gjp):
        for field in list(self._fields.values()):
            field.gjp(gjp)

    def flush(self):
        for field in list(self._fields.values()):
            field.flush()
