

class DefaultMixin(object):
    ######### DEFAULT ########################
    def get_default(self):
        default_value = None
        has_default = False
        try:
            model_field = self.Model._meta.get_field(field_name = self.field_name)
            default_value = model_field.default

            # when it is not provided: default_value = class django.db.models.fields.NOT_PROVIDED
            if type(default_value).__name__.find('NOT_PROVIDED'):  
                default_value = 'not provided'
            else:
                has_default = True
        except:
#             raise FieldDoesNotExist
            default_value = None
        
        self._has_default = has_default
        self._default_value     = default_value
        return self._has_default, self._default_value 
    
    @property
    def has_default(self):
        if hasattr(self, '_' + 'has_default')  == False:
            self.get_default()
        return self._has_default

    
    @property
    def default_value(self):
        if hasattr(self, '_' + 'default_value')  == False:
            self.get_default()
        return self._default_value
    ######### DEFAULT ########################