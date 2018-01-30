from .field import Field
from .enums import ValueStatus, FieldKind

class SequenceField(Field):
    _item_type = None
    
    def __init__(self,
                 database_object,
                 aspect,
                 field_list_locator,
                 kind = FieldKind.regular):
                 
        super(SequenceField, self).__init__(database_object,
                                            aspect,
                                            kind)
        self._field_list_locator = field_list_locator
        self._list = []

    @property
    def status(self):
        if any([item.status == ValueStatus.hard for item in self._list]):
            return ValueStatus.hard
        else:
            return self._status

    def invalidate(self):
        self.flush()
        if self.status is ValueStatus.soft:
            self._status = ValueStatus.none
            self._list = []

    @property
    def value(self):
        if self._status is ValueStatus.none:
            raise RuntimeError("Accessing to field which is not set")
        else :
            return self

    def hard_set(self,
                 value):
        raise NotImplementedError("Is not supported at the moment") #TODO: Shall we support it?

    def update(self,
               gjp):
        if self.status is not ValueStatus.hard:
            found = True
            value = self._master_object(gjp)
            for fname in self._field_list_locator.split("."):
                if fname in value:
                    value = value[fname]
                else :
                    found = False
                    break
            if found:
                if value is None:
                    value = []
                self._list = []
                for item in value:
                    self._list.append(self._item_type.from_gjp(item, self.database_object))
                self._status = ValueStatus.soft
                
    def gjp(self,
            gjp):
        if self.status == ValueStatus.hard:
            cursor = gjp
            for fname in self._field_list_locator.split(".")[:-1]:
                if fname not in cursor:
                    cursor[fname] = {}
                cursor = cursor[fname]
            cursor[self._field_list_locator.split(".")[-1]] = [item.to_gjp() for item in self._list]

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        class readonly_item(object):
            def __init__(self, item):
                self.__dict__['_item'] = item
            def __getattr__(self, name):
                return getattr(self._item, name)
            def __setattr__(self, name, value):
                raise AttributeError("Cannot modify property of readonly field")
            
        items = self._list[key]
        if self.kind is FieldKind.readonly and self.database_object._object_id is not None:
            if isinstance(items, list):
                return [readonly_item(item.value) for item in items]
            else :
                return readonly_item(items.value)
        else:
            if isinstance(items, list):
                return [item.value for item in items]
            else :
                return items.value

    def __setitem__(self, key, value):
        raise RuntimeError("Is not supported at the moment") #TODO: Shall we support it?

    def __delitem__(self, key):
        if self.kind is FieldKind.readonly and self.database_object._object_id is not None:
            raise AttributeError("Cannot assign to readonly field")
        del self._list[key]
        self._status = ValueStatus.hard
        
    def __iter__(self):
        return iter([item.value for item in self._list])

    # def add(self):
    #     self._list.appedn
    #     self._status = ValueStatus.hard

    
class SequenceItem(object):
    def __init__(self,
                 status = ValueStatus.none):
        self._status = status
        self._properties = {}

    @classmethod
    def from_gjp(self,
                 gjp,
                 database_object):
        pass

    def to_gjp(self):
        pass

    @property
    def status(self):
        return self._status

    @property
    def value(self):
        return self

class SequenceItemProperty(object):
    def __init__(self,
                 name):
        self._name = name

    def __set__(self, instance, value):
        instance._properties[self._name] = value
        instance._status = ValueStatus.hard

    def __get__(self, instance, owner):
        return instance._properties[self._name]

