class NullableMixin(object):
    
    def get_is_nullable(self):
        
        null_value = None
        try:
            model_field = self.Model._meta.get_field(field_name = self.field_name)
            null_value = model_field.null
        except:
#             raise FieldDoesNotExist
            null_value = None
        
        self._is_nullable = null_value
        return null_value

    @property
    def is_nullable(self):
        if hasattr(self, '_'+'is_nullable')  == False:
            self.get_is_nullable()
        return self._is_nullable