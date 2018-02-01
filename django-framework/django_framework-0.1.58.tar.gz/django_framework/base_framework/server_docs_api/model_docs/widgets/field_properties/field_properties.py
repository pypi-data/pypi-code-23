
from field_types import ChoicesMixin
from field_types import DefaultMixin

from field_types import EditableMixin
from field_types import ModelTypeMixin

from field_types import NullableMixin

from field_types import SearchableMixin

from field_types import WriteOnceMixin

from field_types import HelpTextMixin

class FieldProperties(ChoicesMixin,
                      DefaultMixin,
                      EditableMixin,
                      ModelTypeMixin,
                      NullableMixin,
                      SearchableMixin,
                      WriteOnceMixin,
                      HelpTextMixin,
                      
                      ):
    
    def __init__(self, Model, Serializer, field_name):
        
        self.Model = Model
        self.Serializer = Serializer
        
        self.field_name = field_name

    
    
    def _get_field(self):

        field_name = self.clean_field_name()
        try:
            model_field = self.Model._meta.get_field(field_name = field_name)
        except: #raise FieldDoesNotExist
            model_field = None

        return model_field

    def _get_internal_type(self):
        field_name = self.clean_field_name()
        try:
            model_field = self.Model._meta.get_field(field_name = field_name)
            model_type =  model_field.get_internal_type()
        except: #raise FieldDoesNotExist
            model_type = None
        
        return model_type

    def clean_field_name(self):
        
        if self.field_name.find('_ids') >=0:
            return self.field_name[:-4]
        
        return self.field_name



    def get_response(self):
        
        field_properties = {
            'is_searchable' : self.is_searchable,
            'is_editable' : self.is_editable,
            'is_write_once' : self.is_write_once,
            
            'column_type' : self.model_type,
            'is_nullable' : self.is_nullable,
#             
#             
            'has_default' : self.has_default,
            'default_value' : self.default_value,
#             
            'has_choices' : self.has_choices,
            'choices' : self.choices,
            
            'help_text' : self.help_text
            }
        
        return field_properties