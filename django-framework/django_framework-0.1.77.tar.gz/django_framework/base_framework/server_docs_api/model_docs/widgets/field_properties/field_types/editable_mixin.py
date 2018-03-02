
class EditableMixin(object):
    
    def get_is_editable(self):
        
        field_type = self.Serializer._declared_fields.get(self.field_name)
        field_type = type(field_type).__name__.lower()

        is_editable = True
        if self.field_name.find('alt') >=0:
            is_editable = False
            
        if field_type == 'SerializerMethodField':
            is_editable = False
            
        if field_type.find('human') >=0:
            is_editable = False
        
        if self.field_name in self.Serializer.Meta.write_once_fields:
            is_editable = False
            
        if self.field_name in self.Serializer.Meta.read_only_fields:
            is_editable = False
        
        self._is_editable = is_editable
        return self._is_editable
    
    @property
    def is_editable(self):
        if hasattr(self, '_'+'is_editable')  == False:
            self.get_is_editable()
        return self._is_editable