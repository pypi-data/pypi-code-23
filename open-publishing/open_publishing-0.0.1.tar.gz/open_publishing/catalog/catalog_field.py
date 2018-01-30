from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field

from . import catalog_types 

class CatalogField(Field):
    def __init__(self,
                 document):
        super(CatalogField, self).__init__(database_object=document,
                                           aspect=":basic" )
        self._value = None

    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError("Accessing to field which is not set")
        else :
            return self._value

    def hard_set(self,
                 value):
        if isinstance(value, catalog_types.Academic):
            self._value = catalog_types.Academic(self._database_object) 
            self._value.hard_set(value)
            self._status = ValueStatus.hard
        elif isinstance(value, catalog_types.NonAcademic):
            self._value = catalog_types.NonAcademic(self._database_object)
            self._value.hard_set(value)
            self._status = ValueStatus.hard
        else :
            raise ValueError("Expected instance of Academic or NonAcademic, got {0}".format(type(value)))

    def update(self,
               gjp):
        master_obj = self._master_object(gjp)
        if self._status is not ValueStatus.hard:
            if 'is_academic' in master_obj:
                if master_obj['is_academic'] == True:
                    self._value = catalog_types.Academic(self._database_object)
                elif master_obj['is_academic'] == False:
                    self._value = catalog_types.NonAcademic(self._database_object)
                else:
                    raise RuntimeError('Unexpected value of is_academic field {0}'.format(master_obj['is_academic']))
                self._status = ValueStatus.soft
        if self._status is not ValueStatus.none:
            self._value.update(gjp)
            
    def gjp(self,
            gjp):
        if self._status is not ValueStatus.none:
            if self._status is ValueStatus.hard:
                if isinstance(self._value, catalog_types.Academic):
                    gjp['is_academic'] = True
                elif isinstance(self._value, catalog_types.NonAcademic):
                    gjp['is_academic'] = False
                else:
                    raise RuntimeError("This is not supposed to happen")
            self._value.gjp(gjp)
