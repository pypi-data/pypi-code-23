import json
from rest_framework import serializers


class JSONField(serializers.Field):
    
    def to_representation(self, value): 
        '''When we are serializing a model to API'''
        if value is None or isinstance(value, dict) or isinstance(value, list):
            response = value
        else:
            try:
                response = json.loads(value)
            except Exception as e:
                print('error converting things to a python object!')
                response = value # we give back what we got!
                
        return response

    def to_internal_value(self, data):
        '''Converting an incoming parameter to be eaten by DB (a TextField)'''
        if data is None:
            response = data
        else:
            try:
                response = json.dumps(data)
            except Exception as e:
                print('error converting things to a python object!', e)
                response = data # we give back what we got!

        return response
