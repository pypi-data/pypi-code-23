# -*- coding: utf-8 -*-

"""
trading212api.exceptions
~~~~~~~~~~~~~~

This module contains all exceptions.
"""


class RequestError(Exception):
    """raised when status_code different from 200"""
    def __init__(self, response):
        if response.status_code == 500:  # internal error
            details = response.json()['context']
            if details['type'] == 'PriceChangedException':  # if price has changed
                raise PriceChangedException(details['current'])
            if details['type'] == 'MinQuantityExceeded':  # if min not respected
                raise MinQuantityExceeded(details['min'])
        super().__init__("Request error %d" % response.status_code)


class PriceChangedException(Exception):
    def __init__(self, price):
        self.price = price
        super().__init__("Price changed to %f" % price)


class MinQuantityExceeded(Exception):
    def __init__(self, min):
        self.min = min
        super().__init__("Below min quantity of %d" % min)
