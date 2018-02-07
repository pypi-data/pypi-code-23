import inspect
import json
from os import path
from typing import Callable, Generator, List

import requests
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from . import processors


class BackofficeException(BaseException):
    pass


class BackofficeHTTPException(BackofficeException):
    pass


class BackofficeValidationError(BackofficeException):
    pass


class BackofficeClient:
    TIMEOUT = 6
    ORDERS_URL = '{HOST}/orders/'
    ITEMS_URL = '{HOST}/orders/{order_id}/items/'

    headers = {
        'Authorization': 'Token {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def __init__(self, url, token):
        self.url = url

        self.headers['Authorization'] = self.headers['Authorization'].format(token=token)

    @staticmethod
    def _get_schema(schema: str):
        filename = path.join(path.dirname(__file__), 'schemas', schema + '.schema.json')

        with open(filename, 'r') as f:
            return json.load(f)

    @classmethod
    def validate_order(cls, order: dict):
        try:
            validate(order, cls._get_schema('order'))

        except ValidationError as e:
            raise BackofficeValidationError(str(e))

        return True

    @classmethod
    def validate_items(cls, items: List):
        try:
            validate(items, cls._get_schema('items'))

        except ValidationError as e:
            raise BackofficeValidationError(str(e))

        return True

    def post_order(self, order: dict) -> dict:
        r = requests.post(self.ORDERS_URL.format(HOST=self.url), json=order, headers=self.headers, timeout=self.TIMEOUT)
        if r.status_code != 201:
            raise BackofficeHTTPException('Non-201 response when creating an order: %d (%s)' % (r.status_code, r.content))

        return r.json()

    def post_items(self, order: dict, items: List):
        r = requests.post(self.ITEMS_URL.format(HOST=self.url, order_id=order['id']), json=items, headers=self.headers, timeout=self.TIMEOUT)
        if r.status_code != 201:
            raise BackofficeHTTPException('Non-201 response when adding items: %d (%s)' % (r.status_code, r.content))

        return r.json()

    @classmethod
    def run_processors(cls, obj, type: str):
        """Runs the processors defined in processors.py"""
        for processor in cls.get_processors(type):
            obj = processor(obj)
            if obj is None:
                raise AttributeError(f'Processor {processor} returned nothing!')

        return obj

    @staticmethod
    def get_processors(type: str) -> Generator[Callable, None, None]:
        for member in inspect.getmembers(processors, lambda member: inspect.isfunction(member) and type in inspect.signature(member).parameters.keys()):
            yield member[1]

    def send(self, order: dict, items: List):
        order = self.run_processors(order, 'order')
        self.validate_order(order)

        order = self.post_order(order)
        if 'id' not in order.keys():
            raise BackofficeException('Incorrect response from backoffice (no order id)')

        items = self.run_processors(items, 'items')
        self.validate_items(items)
        self.post_items(order, items)
        return order
