

class ModelTypeMixin(object):
    def get_model_type(self):
        
        model_type = self._get_internal_type()
        
        if model_type == None:
            model_type = 'derived'
            
        self._model_type = model_type
        return self._model_type
    
    @property
    def model_type(self):
        if hasattr(self, '_'+'model_type')  == False:
            self.get_model_type()
        return self._model_type