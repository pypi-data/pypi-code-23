from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field

class SearchTagsField(Field):
    def __init__(self,
                 document):
        super(SearchTagsField, self).__init__(database_object=document,
                                              aspect='search_tags')
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
            raise TypeError('Expected set of SearchTags, got {0}'.format(type(value)))

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if 'search_tags' in master_obj:
                self._value = {i['keyword'] for i in master_obj['search_tags']}
                self._status = ValueStatus.soft
            
    def gjp(self,
            gjp):
        if self._status is ValueStatus.hard:
            gjp['search_tags'] = [{'keyword' : keyword} for keyword in self._value]

