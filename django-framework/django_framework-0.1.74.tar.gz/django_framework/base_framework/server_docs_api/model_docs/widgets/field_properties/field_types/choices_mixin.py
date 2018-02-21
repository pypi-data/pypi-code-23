'''
Created on Jan 17, 2018

@author: aser
'''
class ChoicesMixin(object):
    ######### CHOICES ########################
    def get_choices(self):
        
        choices = None
        has_choices = False
        
        model_field = self._get_field()
        
        if self.field_name == 'choices_field':
            print(model_field, self.field_name, '<---')
        
        
        if model_field != None:
            choices = model_field.choices
            if type(choices).__name__.find('NOT_PROVIDED') >=0:  
                choices = 'not provided'
            else:
                has_choices = True
        else:
            choices = None

        if self.field_name == 'uuid':
            has_choices, choices = self._override_uuid()

        self._has_choices = has_choices
        self._choices = choices
        
        return self._has_choices, self._choices  
    
    def _override_uuid(self):
        
        return False, 'not_provided'
    
    
    
    @property
    def has_choices(self):
        if hasattr(self, '_' + 'has_choices')  == False:
            self.get_choices()
        return self._has_choices
    
    @property
    def choices(self):
        if hasattr(self, '_' + 'choices')  == False:
            self.get_choices()
        return self._choices
    ######### CHOICES ########################