import logging
from typing import Dict

from jsonschema import validate

from .base import JsonField

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['ValidableJsonField']

_log = logging.getLogger(__name__)


class ValidableJsonField(JsonField):

    def __init__(self, json_scheme: Dict, default=None, **kwargs) -> None:
        super().__init__(default=default, **kwargs)
        self.json_scheme = json_scheme

    def __set__(self, instance, value) -> None:
        if value is not None:
            if not isinstance(value, self.param_type):
                raise ValueError(f'Field {self.name} value should have {str(self.param_type)} type instead of {value}')
            validate(value, self.json_scheme)
        super().__set__(instance, value)
