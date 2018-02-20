#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2018 TUNE, Inc. (http://www.tune.com)
#  @namespace pyhttpstatus_utils

import sys
if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[2] < 5):
    from .http_status_enum import HTTPStatus
else:
    from http import HTTPStatus

if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[2] < 2):
    from repoze.lru import lru_cache
else:
    from functools import lru_cache

from .http_status_type import HttpStatusType

@lru_cache(maxsize=128)
def _create_http_status_dict():
    http_status_dict = {}

    for httpstatus in list(HTTPStatus):
        code = int(httpstatus)
        http_status_dict[code] = {
            "code": code,
            "name": httpstatus.name,
            "phrase": httpstatus.phrase,
            "description": httpstatus.description
        }

    return http_status_dict

@lru_cache(maxsize=128)
def _create_http_status_phrase_dict():
    http_status_dict = {}

    for httpstatus in list(HTTPStatus):
        code = int(httpstatus)
        http_status_dict[code] = httpstatus.phrase

    return http_status_dict

@lru_cache(maxsize=128)
def _create_http_status_code_desc_dict():
    http_status_dict = {}

    for httpstatus in list(HTTPStatus):
        code = int(httpstatus)
        http_status_dict[code] = httpstatus.description

    return http_status_dict

HTTP_STATUS_DICT = _create_http_status_dict()

# Phrases of HTTP status codes.
HTTP_STATUS_PHRASE_DICT = _create_http_status_phrase_dict()
HTTP_STATUS_PHRASE_DICT.update({

    # Client Error.
    418: 'I\'m a Teapot',  # RFC 2324 April Fool's Joke
    419: 'Authentication Timeout',  # RFC 2616 not part of HTTP standard
    425: 'Unordered Collection',  # Defined in drafts of "WebDAV Advanced Collections Protocol"
    440: 'Login Timeout',  # Microsoft
    444: 'No Response',  # Nginx
    449: 'Retry With',  # Microsoft
    450: 'Blocked By Windows Parental Controls',  # Microsoft
    451: 'Unavailable For Legal Reasons',  # Internet Draft http://en.wikipedia.org/wiki/HTTP_451
    494: 'Request Header Too Large',  # Nginx
    495: 'Cert Error',  # Nginx
    496: 'No Cert',  # Nginx
    497: 'HTTP to HTTPS',  # Nginx
    499: 'Client Closed Request'  # Nginx

    # Server Error.
    # 509: 'This status code, while used by many servers, is not specified in any RFCs.'
})

# Descriptions of HTTP status codes.
HTTP_STATUS_DESC_DICT = _create_http_status_code_desc_dict()
HTTP_STATUS_DESC_DICT.update({

    # Client Error.
    418: 'HTCPCP server is a teapot; the resulting entity body may be short and stout.',
    419: 'Authentication Timeout denotes that previously valid authentication has expired.',
    425: 'Attempted to set the position of an internal collection member in a collection with a server-maintained ordering',
    440: 'Your session has expired. (Microsoft)',
    444: 'Server has returned no information to the client and closed the connection (Ngnix).',
    449: 'Request should be retried after performing the appropriate action (Microsoft).',
    450: 'Windows Parental Controls are turned on and are blocking access to the given webpage.',
    451: (
        'You attempted to access a Legally-restricted Resource. This could be due to censorship or ' +
        'government-mandated blocked access.'
    ),
    494: 'Nginx internal code',
    495: 'SSL client certificate error occurred. (Nginx)',
    496: 'Client did not provide certificate (Nginx)',
    497: 'Plain HTTP request sent to HTTPS port. (Nginx)',
    499: 'Connection has been closed by client while the server is still processing its request (Nginx).'

    # Server Error.
    # 509: 'This status code, while used by many servers, is not specified in any RFCs.'
})

HTTP_STATUS_TYPE_DICT = {
    100: HttpStatusType.INFORMATIONAL,
    200: HttpStatusType.SUCCESSFUL,
    300: HttpStatusType.REDIRECTION,
    400: HttpStatusType.CLIENT_ERROR,
    500: HttpStatusType.SERVER_ERROR
}
