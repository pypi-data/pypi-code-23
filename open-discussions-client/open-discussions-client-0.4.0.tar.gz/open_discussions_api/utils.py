"""API utils"""
import time

import jwt

EXPIRATION_DELTA_SECONDS = 60 * 60


def get_token(secret, username, roles, expires_delta=EXPIRATION_DELTA_SECONDS, extra_payload=None):
    """
    Gets a JWt token

    Args:
        username (str): user's username
        roles (list(str)): list of roles
        expires_delta (int): offset in second of token expiration
        extra_payload (dict): dictionary of extra payload properties to encode in the token

    Returns:
        str: encoded JWT token
    """
    now = int(time.time())
    payload = {
        'username': username,
        'roles': roles,
        'exp': now + expires_delta,
        'orig_iat': now,
    }

    invalid_extras = set(payload).intersection(extra_payload or {})
    if invalid_extras:
        raise AttributeError('Invalid arguments for payload: {}'.format(invalid_extras))

    if extra_payload:
        payload.update(extra_payload)
    return jwt.encode(payload, secret, algorithm='HS256').decode('utf-8')
