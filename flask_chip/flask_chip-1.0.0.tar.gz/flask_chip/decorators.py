# -*- coding: utf-8 -*-
'''
The decorator function for guarding flask view functions
'''

from functools import wraps, partial

from flask import request, current_app as app
from pyresult import is_ok, rmap
from toolz import pipe

from .utils import save_user, unauthorized
from .tokens import verify as verify_token


def verify(fun, pipeline, on_error):
    '''Run given pipeline, when result is ok run decorated function
    otherwise run on_error function

    :param fun: guarded function
    :param pipline: token proccesing pipeline
    :param on_error: function called when pipeline result is error
    :returns: function
    '''
    @wraps(fun)
    def _verify(*args, **kwargs):
        result = pipe(*pipeline)
        return fun(*args, **kwargs) if is_ok(result) else on_error()

    return _verify


def create_verify_user(get_user, header_key='X-Auth-Token', on_error=unauthorized):
    '''Create user verify decorator.

    :param get_user: function that returns user object based on data from the token
    :param header_key: token header field name
    :param on_error: function called when pipeline result is error
    :returns: user verify decorator
    '''
    pipeline = (
        header_key,
        lambda key: request.headers.get(key, ''),
        lambda token: verify_token(token, app.config['SECRET_KEY']),
        rmap(get_user),  # pylint: disable=no-value-for-parameter
        rmap(save_user),  # pylint: disable=no-value-for-parameter
    )

    return partial(verify, pipeline=pipeline, on_error=on_error)


def create_verify_single_use_token(
        exists_and_remove,
        header_key='X-Single-Use-Token',
        on_error=unauthorized
):
    '''Create one-time-access token verify decorator

    :param exists_and_remove: function that return key when exists in store and remove it
    :param header_key: token header field name
    :param on_error: function called when pipeline result is error
    :returns: token exists decorator
    '''
    pipeline = (
        header_key,
        lambda key: request.headers.get(key, ''),
        exists_and_remove,
        lambda token: verify_token(token, app.config['SECRET_KEY']),
    )

    return partial(verify, pipeline=pipeline, on_error=on_error)
