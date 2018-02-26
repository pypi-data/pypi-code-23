# coding=utf-8
"""
Computes hashes
"""

import hashlib

from elib import custom_logging

LOGGER = custom_logging.get_logger('ELIB')


def get_hash(data, method: str = 'md5'):
    """
    Computes hash from data

    Args:
        data: data
        method: hash method (defaults to MD5) One of [sha1, sha224, sha256, sha384, sha512, blake2b, blake2s]

    Returns: hash value

    """
    if not isinstance(data, bytes):
        data = bytes(data, 'utf-8')

    try:
        func = getattr(hashlib, method)
    except AttributeError:
        raise RuntimeError('cannot find method "{}" in hashlib'.format(method))
    else:
        hash_ = func(data).hexdigest()
        LOGGER.debug('hash for binary data: %s', hash_)

        return hash_
