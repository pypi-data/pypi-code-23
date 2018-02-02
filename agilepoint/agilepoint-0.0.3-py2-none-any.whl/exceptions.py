"""Custom Exceptions for AgilePoint"""
from __future__ import print_function
import logging

class MissingRequiredArg(Exception):
    """Exception for missing required argument."""
    def __init__(self, message):
        super(MissingRequiredArg, self).__init__(message)
        self.message = message
    def __repr__(self):
        print('Missing required argument: {0}'.format(self.message))

class InvalidArg(Exception):
    """Exception for argument that should not be there."""
    def __init__(self, message):
        super(InvalidArg, self).__init__(message)
        self.message = message
    def __repr__(self):
        print('Invalid argument: {0}'.format(self.message))

class AgilePointBadResponse(Exception):
    """Exception for handling bad responses other than 200"""
    def __init__(self, url, status_code, text):
        super(AgilePointBadResponse, self).__init__(url, status_code, text)
        self.url = url
        self.status_code = status_code
        self.text = text
    def __repr__(self):
        message = '{} {}: {}'.format(self.url, self.status_code, self.text)
        print(message)
        logging.error(message)
