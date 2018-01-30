from .enums import ValueStatus, FieldKind

class FieldDescriptor(object):
    def __init__(self,
                 name):
        self._name = name

    def __set__(self, instance, value):
        field = instance._fields[self._name]
        if field.kind is FieldKind.readonly and field.database_object is not None and field.database_object._object_id is not None:
            raise AttributeError("Cannot assign to readonly field")
        else:
            field.hard_set(value)
            if field.database_object:
                field.database_object._on_changed() #TODO: consider doing it
                                                    #somewhere else
                                                    #(e.g. in each hard_set())

    def __get__(self, instance, owner):
        field = instance._fields[self._name]
        if field.status in [ValueStatus.soft, ValueStatus.hard, ValueStatus.default]:
            return field.value
        elif (field.database_object is None or field.database_object._object_id is None) and field.status is ValueStatus.none:
           return None
        else:
            field.database_object._fetch([field.aspect])
            if field.status is ValueStatus.soft:
                return field.value
            else:
                raise RuntimeError("seems like wrong field aspect or field locator, name {0}, aspect: {1}".format(self._name,
                                                                                                                  field.aspect))

