#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2018 TUNE, Inc. (http://www.tune.com)
#  @namespace safe_cast

__title__ = 'safe-cast'
__version__ = '0.2.7'
__version_info__ = tuple(__version__.split('.'))

__author__ = 'jefft@tune.com'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2018 TUNE, Inc.'

__python_required_version__ = (3, 0)


def safe_cast(val, to_type, default=None):
    """Safely cast a value to type, and if failed, returned default if exists.
    Optional: Pass default value. Returned if casting fails.

    :param val: Value to be cast.
    :param to_type: Safely cast to a specific type.
    :param default: Default if casting fails.
    :return: Return casted value or default.
    """
    if val is None:
        return default

    try:
        return to_type(val)
    except ValueError:
        if default is None:
            raise
        return default


def safe_str(val, default=None):
    """Safely cast a value to a string.
    Optional: Pass default value. Returned if casting fails.

    :param val: Value to be cast to string.
    :param default: Default if casting fails.
    :return: Return string casted value or default.
    """
    if val is None:
        return default if default is not None else ''

    return safe_cast(val, str, default)


def safe_float(val, ndigits=2, default=None):
    """Safely cast a value to float, remove ',' if exists to ensure strings "1,234.5" are transformed to become "1234.5".
    Optional: Pass default value. Returned if casting fails.

    :param val: Value to be cast to float.
    :param ndigits: Number of digits in float.
    :param default: Default if casting fails.
    :return: Return float casted value or default.
    """
    if not val:  # None or '' or ""
        return default if default is not None else 0.0

    _val = val.replace(',', '') if type(val) == str else val
    return round(safe_cast(_val, float, default), ndigits)


def safe_int(val, default=None):
    """Safely cast a value to an integer.
    Optional: Pass default value. Returned if casting fails.

    :param val: Value to be cast to int.
    :param default: Default if casting fails.
    :return: Return int casted value or default.
    """
    if not val:  # None or '' or ""
        return default if default is not None else 0

    return safe_cast(safe_float(val, ndigits=0, default=default), int, default)


def safe_dict(val, default=None):
    """Safely cast a value to a dictionary.
    Optional: Pass default value. Returned if casting fails.

    :param val: Value to be cast to dictionary.
    :param default: Default if casting fails.
    :return: Return dictionary casted value or default.
    """
    if not val:  # None or '' or ""
        return default if default is not None else {}

    return safe_cast(val, dict, default)


def safe_smart_cast(val):
    """Safely cast a value to the best matching type.
    Optional: Pass default value. Returned if casting fails.

    :param val: Value to be smartly cast.
    :return: Typed value
    """
    to_type = type(val)
    if to_type == str:
        return safe_str(val)
    if to_type == dict:
        return safe_dict(val)
    if to_type == int:
        return safe_int(val)
    if to_type == float:
        return safe_float(val)

    return safe_str(str(val))


def safe_cost(val):
    """Safety cast value to a cost value which is a floating value with 4 digits.

    :param val: Value to be cast to cost of type float.
    :return: float
    """
    return safe_float(val, ndigits=4)
