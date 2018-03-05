

class HelpTextMixin(object):
    
    
    def get_help_text(self):
        
        field = self._get_field()
        
        
        
        if field == None:
            help_text = 'field is derived'
        else:
            help_text = field.help_text
        
        self._help_text = help_text
        return self._help_text
    
    @property
    def help_text(self):
        if hasattr(self, '_'+'help_text')  == False:
            self.get_help_text()
        return self._help_text