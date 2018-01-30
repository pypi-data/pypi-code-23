from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field

class AdminSearchTagsField(Field):
    def __init__(self,
                 document):
        super(AdminSearchTagsField, self).__init__(database_object=document,
                                                   aspect='admin_search_tags')
        self._value = None
    
    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self._value.copy()

    def hard_set(self,
                 value):
        if isinstance(value, set):
            for i in value:
                if not isinstance(i, str):
                    raise TypeError('Expected set of strings, got {0}'.format(type(i)))
            self._value = value
            self._status = ValueStatus.hard
        else :
            raise TypeError('Expected set of adminSearchTags, got {0}'.format(type(value)))

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if 'admin_search_tags' in master_obj:
                self._value = set(master_obj['admin_search_tags'])
                self._status = ValueStatus.soft
            
    def gjp(self,
            gjp):
        if self._status is ValueStatus.hard:
            gjp['admin_search_tags'] = list(self._value)

