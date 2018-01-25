''' Masonite Validator Module '''

from validator import *

class Validator(object):
    ''' Validator Class '''
    def __init__(self, request):
        self.request = request
        self.request_check = {}
        self.validation_dictionary = {}

    def validate(self, dictionary):
        ''' Sets the validation dictionary '''
        self.validation_dictionary = dictionary
        return self

    def check(self):
        ''' Validated the dictionary '''
        return self.run_validation()[0]

    def errors():
        ''' Returns Errors '''
        return self.run_validation()[1]

    def run_validation(self):
        self.load_request_input()
        return validate(self.validation_dictionary, self.load_request_input())

    def load_request_input(self):
        ''' Need to load request input into a different value
            Since the Request class stores input values as string, we
                need to create a new dictonary value from the request
        '''
        dictionary = {}
        for value in self.request.all():
            dictionary[value] = self.request.input(value)
        return dictionary
