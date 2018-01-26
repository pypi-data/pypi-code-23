# -*- coding: utf-8 -*-

import functools
import logging
import os
import time
from hashlib import sha256

import psutil

__all__ = [
    'timeit',
    'memory',
    'memoize',
]


def timeit(method):
    """ A decorator to measure the time spent by a function.
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        logging.debug('Function: {}: {:.2f} sec'.format(method.__name__, te - ts))
        return result

    return timed


def memory(method):
    """ A decorator to measure the memory before and after the function
    """

    def memory_usage_psutil(*args, **kw):
        process = psutil.Process(os.getpid())
        logging.debug(
            'Function: {} before Memory: {:.2f} MB'.format(method.__name__, process.memory_info()[0] / float(2 ** 20)))
        result = method(*args, **kw)
        logging.debug(
            'Function: {} after Memory: {:.2f} MB'.format(method.__name__, process.memory_info()[0] / float(2 ** 20)))
        return result

    return memory_usage_psutil


def memoize(obj):
    """Memoizer"""
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = sha256((str(args) + str(kwargs)).encode('utf-8'))
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer
