from abc import ABCMeta, abstractmethod

import validators as v

class Validator():
    
    def __init__(self, input_name=None):
            
        self.input_name = input_name if input_name else 'Input'
    
    @abstractmethod
    def validate(self, input):
        pass
    
class ValidatorException(Exception):
    pass

class Email(Validator):
    
    def validate(self, input):
        
        if v.email(input):
            return True
        
        raise ValidatorException('{input} is not a valid {input_name}'.format(input=input, input_name=self.input_name))