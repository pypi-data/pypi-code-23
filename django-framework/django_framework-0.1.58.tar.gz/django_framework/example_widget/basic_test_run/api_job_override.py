import copy

# this is where we hold basic things
from django_framework.django_helpers.api_helpers import BaseAPI
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer
 
 
from django.contrib.auth.models import User

from django_framework.helpers.security_helpers import generate_unique_key

 
from django_framework.base_framework.model_jobs_api.api import ModelJobAPI

from django_framework.django_helpers.api_helpers import register_api

class BasicTestRunJobAPI(ModelJobAPI):
    '''The name of this is very specific and allows us to override the django_framework.base_framework version of ModelAPI'''
 
    def __init__(self, **kwargs):
        kwargs['run'] = False
         
        self.model_name = 'BasicTestRun'
        super(BasicTestRunJobAPI, self).__init__(**kwargs)
 
    def get(self):
        print('hahahahahha')
        
        return super(BasicTestRunJobAPI, self).get()

register_api(BasicTestRunJobAPI)