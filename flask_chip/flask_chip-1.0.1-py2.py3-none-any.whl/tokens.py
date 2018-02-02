# -*- coding: utf-8 -*-
'''
Generate token and verify
'''

from time import time
from itsdangerous import (
    SignatureExpired,
    BadSignature,
    JSONWebSignatureSerializer as Serializer
)
from pyresult import ok, error, rmap, and_then, with_default
from toolz import pipe


def generate(data, key, **kwargs):
    ''' Generate JWT token with supplied data

    **Examples**

    >>> from flask_chip.tokens import generate, verify

    >>> key = "y):'QGE8M-b+MEKl@k4e<;*9.BqL=@~B"
    >>> data = {'foo': 1234}
    >>> token = generate(data, key)
    >>> verify(token, key)
    Result(status='Ok', value={'foo': 1234})
    '''
    iat = kwargs.get('iat', _now())
    exp = kwargs.get('exp', 24 * 60 * 60)

    claim = {
        'data': data,
        'iat': iat,
        'exp': _expires_in(iat, exp),
    }

    serializer = Serializer(key)
    token = serializer.dumps(claim, header_fields={'typ': 'JWT'})
    return token.decode('utf-8')


def verify(token, key):
    ''' Check the supplied token and it's expiration.

    :param token: A token to verify
    :param key: decryption key
    :returns: result with data

    **Examples**

    returns data if token is valid

    >>> from flask_chip.tokens import generate, verify

    >>> key = "y):'QGE8M-b+MEKl@k4e<;*9.BqL=@~B"
    >>> data = {'foo': 1234}
    >>> token = generate(data, key=key)
    >>> verify(token, key=key)
    Result(status='Ok', value={'foo': 1234})

    returns expiration error when token expire

    >>> from time import sleep

    >>> key = "y):'QGE8M-b+MEKl@k4e<;*9.BqL=@~B"
    >>> data = {'foo': 1234}
    >>> token = generate(data, key=key, exp=0)
    >>> sleep(1)  # wait for token expiration
    >>> verify(token, key=key)
    Result(status='Error', value='Token expired.')

    returns time travele error

    >>> from time import time

    >>> iat = time() + 3600
    >>> key = "y):'QGE8M-b+MEKl@k4e<;*9.BqL=@~B"
    >>> data = {'foo': 1234}
    >>> token = generate(data, key=key, iat=iat)
    >>> verify(token, key=key)
    Result(status='Error', value='Token traveled through time.')

    returns error if token is invalid

    >>> key = "y):'QGE8M-b+MEKl@k4e<;*9.BqL=@~B"
    >>> data = {"foo": 1234}
    >>> token = generate(data, key=key)
    >>> key2 = "12345678901234567890123456789012"
    >>> verify(token, key=key2)
    Result(status='Error', value='invalid JWT')
    '''
    serializer = Serializer(key)
    try:
        return pipe(
            token,
            serializer.loads,
            ok,
            and_then(_expired),  # pylint: disable=no-value-for-parameter
            and_then(_time_traveled),  # pylint: disable=no-value-for-parameter
            rmap(lambda d: d['data'])  # pylint: disable=no-value-for-parameter
        )
    except (SignatureExpired, BadSignature, TypeError):
        return error('invalid JWT')


def to_value(res):
    ''' Transform result to `value`,
    if result is `Ok` or `None` in case of `Error`

    :param res: result
    :returns: value or None

    **Examples**

    >>> from pyresult import ok, error
    >>> from flask_chip.tokens import to_value

    returns value if ok

    >>> to_value(ok(12345))
    12345

    returns None if error

    >>> to_value(error('Foo bar baz')) is None
    True
    '''
    return with_default(None, res)


def verify_to_value(*args, **kwargs):
    ''' Verify token and return `data` or `None`

    For params look at :func:`verify`
    and for return value look at :func:`to_value`.
    '''
    return to_value(verify(*args, **kwargs))


def _expires_in(issued_at, expires_in):
    return issued_at + expires_in


def _now():
    return round(time())


def _expired(data):
    return ok(data) if data['exp'] >= _now() else error('Token expired.')


def _time_traveled(data):
    return ok(data) if data['iat'] <= _now() else error('Token traveled through time.')
