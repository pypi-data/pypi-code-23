#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2018 TUNE, Inc. (http://www.tune.com)
#  @namespace pyhttpstatus_utils

"""
HTTP Status Codes and Support Functions.
"""

import copy

from .http_status_dicts import (
    HTTP_STATUS_PHRASE_DICT,
    HTTP_STATUS_DESC_DICT,
    HTTP_STATUS_DICT,
    HTTP_STATUS_TYPE_DICT
)

from .http_status_type import HttpStatusType

class InvalidHttpCode(Exception):
    pass


def validate_http_code(http_code, minimum=100, maximum=599, strict=True, default_http_code=0):
    """Validate HTTP code. If strict, throw, else just return default_http_code."""
    try:
        http_code = int(http_code)
    except:
        if strict:
            raise InvalidHttpCode('[{}] {}  is not a valid integer'.format(http_code, type(http_code)))
        else:
            return default_http_code

    if http_code < minimum:
        if strict:
            raise InvalidHttpCode('{} is below minimum HTTP status code {}'.format(http_code, minimum))
        else:
            return default_http_code
    elif http_code > maximum:
        if strict:
            raise InvalidHttpCode('{} is above maximum HTTP status code {}'.format(http_code, maximum))
        else:
            return default_http_code
    return http_code


def create_http_status_dict(override_dict=None):
    """HTTP Status Dictionary with Overrides if provided.

    Args:
        override_dict:

    Returns:

    """
    dict_ = copy.deepcopy(HTTP_STATUS_PHRASE_DICT)

    if override_dict and isinstance(override_dict, dict) and len(override_dict) > 0:
        for key, value in override_dict.items():
            if key in dict_:
                http_status = dict_[key].rstrip('\.')
                dict_[key] = "{}: {}".format(http_status, value).rstrip('\.') + '.'
            else:
                dict_.update({key: value})

    return dict_

def get_http_status_name(http_status_code):
    """Get HTTP status code description.

    Args:
        http_status_code:

    Returns:

    """
    validate_http_code(http_status_code)
    if http_status_code not in HTTP_STATUS_DICT:
        return None

    return HTTP_STATUS_DICT[http_status_code]['name']


def get_http_status_phrase(http_status_code):
    """Get HTTP status code phrase.

    Args:
        http_status_code:

    Returns:

    """
    validate_http_code(http_status_code)
    if http_status_code not in HTTP_STATUS_PHRASE_DICT:
        if http_status_code not in HTTP_STATUS_DICT:
            return get_http_status_type(http_status_code)

        return HTTP_STATUS_DICT[http_status_code]['phrase']

    return HTTP_STATUS_PHRASE_DICT[http_status_code]


def get_http_status_desc(http_status_code):
    """Get HTTP status code description.

    Args:
        http_status_code:

    Returns:

    """
    validate_http_code(http_status_code)
    if http_status_code not in HTTP_STATUS_DESC_DICT:
        if http_status_code not in HTTP_STATUS_DICT:
            return get_http_status_type(http_status_code)

        return HTTP_STATUS_DICT[http_status_code]['description']

    return HTTP_STATUS_DESC_DICT[http_status_code]


def get_http_status_type(http_status_code):
    """Get HTTP Status Code Type

    Args:
        http_status_code:

    Returns:

    """
    validate_http_code(http_status_code)
    http_status_code_base = int(http_status_code / 100) * 100

    return HTTP_STATUS_TYPE_DICT[http_status_code_base]


def is_http_status_type(http_status_code, http_status_type):
    """Match if provided HTTP Status Code is expected
    HTTP Status Code Type.

    Args:
        http_status_code:
        http_status_type:

    Returns:

    """
    return get_http_status_type(http_status_code) == http_status_type


def is_http_status_successful(http_status_code):
    """Check if HTTP Status Code is type Successful

    Args:
        http_status_code:
        logger:

    Returns:

    """
    return is_http_status_type(http_status_code=http_status_code, http_status_type=HttpStatusType.SUCCESSFUL)
