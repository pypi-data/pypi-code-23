from .enums import ValueStatus, FieldKind

class Field(object):
    def __init__(self,
                 database_object,
                 aspect = None,
                 kind = FieldKind.regular):
        self._database_object = database_object
        self._aspect = aspect
        if database_object is None:
            self._status = ValueStatus.default
        else:
            self._status = ValueStatus.none
        self._kind = kind

    @property
    def database_object(self):
        return self._database_object

    @property
    def kind(self):
        return self._kind

    @property
    def status(self):
        return self._status

    @property
    def aspect(self):
        return self._aspect

    @property
    def value(self):
        raise NotImplementedError("propery 'value' should be redefined in derived class")
    
    def hard_set(self,
                 value):
        raise NotImplementedError("function 'hard_set' should be redefined in derived class")

    def invalidate(self):
        self.flush()
        if self._status is ValueStatus.soft:
            self._status = ValueStatus.none


    def update(self,
               gjp):
        raise NotImplementedError("function 'update' should be redefined in derived class")

    def gjp(self,
            gjp):
        raise NotImplementedError("function 'gjp' should be redefined in derived class")

    def flush(self):
        pass

    def _master_object(self, gjp):
        return gjp.get(self.database_object.guid, {})

    
