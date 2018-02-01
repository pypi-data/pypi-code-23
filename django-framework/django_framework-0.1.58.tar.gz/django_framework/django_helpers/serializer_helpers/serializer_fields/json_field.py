import json
from rest_framework import serializers


class JSONField(serializers.Field):
    
    def to_representation(self, value): 
        '''When we are serializing a model to API'''
        if value is None or isinstance(value, dict) or isinstance(value, list):
            response = value
        else:
            response = json.loads(value)
        
        return response

    def to_internal_value(self, data):
        '''Converting an incoming parameter to be eaten by DB (a TextField)'''
        if data is None:
            response = data
        else:
            response = json.dumps(data)
        return response
