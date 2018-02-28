"""
The processors work like a hybrid of pytest fixtures and middleware.

To define an order processor, you should create a function with a signle argument 'order'
To defined an items list process, you should create a function with a single argument 'items'

All processors are executed sequentially
"""
from collections import Iterable


def p01_format_date(order):
    """
    Format a russian date dd.mm.yyyy to computer-readble yyyy-mm-dd.

    Attention! This function dropes unparsable dates
    """
    def process(date):
        if '-' in date and len(date) == 10:
            return date

        if '.' in date and len(date) == 10:  # russian format dd.mm.yyyy to yyyy-mm-dd
            dmy = date.split('.')
            if len(dmy) == 3 and all(v is not None for v in dmy):
                return '-'.join(reversed(dmy))

    if 'delivery' in order and 'desired_date' in order['delivery']:
        order['delivery']['desired_date'] = process(order['delivery']['desired_date'])

    return order


def p99_drop_keys_without_values(order):
    for key, value in order.copy().items():
        if isinstance(value, dict):
            order[key] = p99_drop_keys_without_values(value)

        if value is None or (isinstance(value, Iterable) and len(value) == 0):
            del order[key]

    return order
