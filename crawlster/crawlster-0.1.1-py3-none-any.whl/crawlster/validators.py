"""This module contains various validators.

They are used mainly in the config options definitions.
"""
import urllib.parse


class ValidationError(Exception):
    """Thrown when validation fails"""


class ValidateIsInstance(object):
    """Validates that a value is of certain type"""

    def __init__(self, req_type):
        """Initializes the validator

        Args:
            req_type (type or tuple):
                a single type or a tuple of type instances to check against
        """
        self._type = req_type

    def __call__(self, value):
        """Performs the actual validation"""
        if not isinstance(value, self._type):
            raise ValidationError(
                'Expected type {} byt got {} instead'.format(
                    self._type, type(value).__name__
                ))


# legacy
validate_isinstance = ValidateIsInstance


def one_of(choices):
    """Validates that an instance is one of the specified values"""

    def actual_validator(value):
        if value not in choices:
            raise ValidationError(
                'Expected one of {} but got {} instead'.format(
                    ', '.join((str(c) for c in choices)), value
                ))

    return actual_validator


def is_url(value):
    """Validates that the value represents a valid URL"""
    result = urllib.parse.urlparse(value)
    if result.scheme and result.netloc:
        return True
    else:
        raise ValidationError('Invalid URL: {}'.format(value))
