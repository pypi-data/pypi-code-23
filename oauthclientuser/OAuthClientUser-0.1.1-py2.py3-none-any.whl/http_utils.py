#!/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


logger = logging.getLogger(__name__)


def get_request(url, headers):
    r = requests.get(url, headers=headers)
    return r.status_code, r.content


def post_request(url, content, username, password):
    print(content)
    if isinstance(content, dict):
        body = urlencode(content)
    else:
        body = content

    print('body: {}'.format(body))
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": '{}'.format(len(body))
    }

    rsp = requests.post(url, data=body, headers=headers, auth=(username, password))
    return rsp.status_code, rsp.content


def get_account_info(url, token_type, access_token):
    headers = {
        'Authorization': '{} {}'.format(token_type, access_token),
        'Accept': 'application/json'
    }

    return get_request(url, headers)
