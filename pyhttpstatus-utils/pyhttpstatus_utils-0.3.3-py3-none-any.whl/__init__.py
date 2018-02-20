#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2018 TUNE, Inc. (http://www.tune.com)
#  @namespace pyhttpstatus_utils

__title__ = 'pyhttpstatus-utils'
__version__ = '0.3.3'
__version_info__ = tuple(__version__.split('.'))

__author__ = 'jefft@tune.com'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2018 TUNE, Inc.'

import sys
if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[2] < 5):
    from .http_status_enum import HTTPStatus

from .http_status_dicts import (
    HTTP_STATUS_PHRASE_DICT,
    HTTP_STATUS_DESC_DICT,
    HTTP_STATUS_DICT,
    HTTP_STATUS_TYPE_DICT
)

from .http_status_code import HttpStatusCode
from .http_status_type import (
    HttpStatusType,
    HttpStatusCodeType
)

from .http_status_methods import (
    create_http_status_dict,
    get_http_status_name,
    get_http_status_phrase,
    get_http_status_desc,
    get_http_status_type,
    is_http_status_type,
    is_http_status_successful,
    validate_http_code
)
