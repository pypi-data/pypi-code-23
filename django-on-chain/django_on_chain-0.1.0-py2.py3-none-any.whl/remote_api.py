import logging

import requests

from . import SETTINGS
from .exceptions import ServerError

logger = logging.getLogger(__name__)


def send_request(
        method,
        url,
        data=None,
        json=None,
        params=None,
        files=None,
        headers=None,
        expected_content_type='application/json',
        expected_error_statuses=None,
        timeout=None):

    timeout = timeout or SETTINGS['DEFAULT_TIMEOUT']
    if isinstance(method, str):
        method = getattr(requests, method)

    try:
        response = method(url, headers=headers, data=data, json=json, files=files, params=params, timeout=timeout)
    except requests.Timeout:
        logger.exception('API call timed out')
        raise ServerError()

    check_response_for_errors(response, expected_content_type, expected_error_statuses)
    return response


def check_response_for_errors(
        response,
        expected_content_type='application/json',
        expected_error_statuses=None):

    if response.headers.get('content-type') != expected_content_type:
        logger.error('Invalid content-type returned: {}'.format(response.headers.get('content-type')),
                     exc_info={
                         'url': response.url,
                         'request_body': response.request.body,
                     })
        raise ServerError()

    if response.status_code >= 400 and response.status_code not in (expected_error_statuses or []):
        logger.error('Unexpected status code returned: {}'.format(response.status_code),
                     exc_info={
                         'url': response.url,
                         'request_body': response.request.body,
                     })
        raise ServerError()
