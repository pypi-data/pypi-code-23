
from django_framework.django_helpers.api_helpers import BaseAPI

from django_framework.django_helpers.model_helpers.model_registry import get_model
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer
from django_framework.django_helpers.worker_helpers.worker_registry import get_worker
from django_framework.django_helpers.meta_helpers.meta_registry import get_meta


from widgets.field_properties import FieldProperties

class ModelDocAPI(BaseAPI):
    
    def __init__(self, request, model_name, **kwargs):
        
        kwargs['request_requires_authentication'] = False # we want to check later!
        
        super(ModelDocAPI, self).__init__(request=request, **kwargs)

        self.model_name = model_name
        
        self.Model = get_model(model_name = self.model_name)
        self.Serializer = get_serializer(self.model_name, version = self.version)
        self.Meta = get_meta(meta_name = self.model_name)
        
        if self.version == 'admin':
            pass

    def get_model_docs(self):

        response = {}
        response['jobs']   = self.get_model_jobs()
        response['description']   = self.get_model_description()
        response['fields'] = self.get_fields()
        response['methods'] = self.get_allowed_method()
        self.response = response
    
    def get_fields(self):
        field_dict = {}
        for field_name in self.Serializer.Meta.fields:
            field_dict[field_name] = FieldProperties(Model = self.Model, Serializer = self.Serializer, field_name = field_name).get_response()
        return field_dict

    
    def get_model_jobs(self):
        
        ModelWorker =  get_worker(self.model_name)
        
        if ModelWorker.ALLOWED_JOBS == None:
            return [] # there are no jobs associated with the model
        
        return ModelWorker.ALLOWED_JOBS.get_allowed_jobs_doc()
        
    
    def get_model_description(self):
        
        return self.Model.get_description_doc()
    
    
    def get_response(self):
        '''Override BaseAPI version of get_response to get autoformatting of data'''
        return self.format_data(data = self.response)
    
    def format_data(self, data):

        return dict(data=data, meta_data = {'type' : 'docs', "total_query_results": 1, 'model' : self.model_name})
    
    
    def get_allowed_method(self):
        ''''''
        return dict(default = self.Meta.ALLOWED_DEFAULT, 
                  requires_authentication = self.Meta.DEFAULT_REQUIRE_AUTHENTICATION)
    