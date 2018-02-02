"""General utilities that don't fit into any other module"""
# import datetime
import requests
from .exceptions import MissingRequiredArg, InvalidArg, AgilePointBadResponse
# pylint: disable=no-member

def handle_response(resp_type, resp):
    """Correctly handle api response and return correct response"""
    if resp.status_code == requests.codes.ok:
        if resp_type == 'bool':
            return True
        elif resp_type == 'json':
            return resp.json()
        elif resp_type == 'text':
            return resp.text
        elif resp_type == 'xml':
            return resp.text
    else:
        raise AgilePointBadResponse(resp.url, resp.status_code, resp.text)


def validate_args(kwargs, req_args=None, opt_args=None):
    """Validate kwargs against provided req_args and opt_args"""
    present_args = kwargs.keys()
    if isinstance(req_args, (tuple, list)):
        for arg in req_args:
            if arg not in present_args:
                raise MissingRequiredArg(arg)
    if isinstance(opt_args, (tuple, list)):
        for arg in present_args:
            if arg not in opt_args:
                raise InvalidArg(arg)
    return True
