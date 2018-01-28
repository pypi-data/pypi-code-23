# -*- coding: utf-8 -*-
from watson.validators import abc


class SuppliedValues(abc.Validator):

    """Validate that a value exists in the list of supplied values.

    Example:

    .. code-block:: python

        validator = Length(1, 10)
        validator('Test')  # True
        validator('Testing maximum')  # raises ValueError
    """

    message = None

    def __init__(self, message='"{value}" is not a valid option.'):
        self.message = message

    def __call__(self, value, **kwargs):
        iterable = (tuple, list)
        if not isinstance(value, iterable):
            value = [value]
        if not set(value).issubset(set(kwargs['field'].actual_values)):
            value = ', '.join(str(v) for v in value) if isinstance(value, iterable) else value
            raise ValueError(self.message.format(value=value))
        return True
