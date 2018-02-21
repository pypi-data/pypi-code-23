
class SearchableMixin(object):
    
    def get_is_searchable(self):

        field_type = self.Serializer._declared_fields.get(self.field_name)
        field_type = type(field_type).__name__.lower()

        is_searchable = True
        if self.field_name.find('alt') >=0:
            is_searchable = False
            
        if field_type == 'serializermethodfield':
            is_searchable = False
            
        if field_type.find('human') >=0:
            is_searchable = False
            
        self._is_searchable = is_searchable
        return self._is_searchable
    
    @property
    def is_searchable(self):
        if hasattr(self, '_'+'is_searchable')  == False:
            self.get_is_searchable()
        return self._is_searchable