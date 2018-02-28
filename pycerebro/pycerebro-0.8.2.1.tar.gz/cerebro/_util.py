# Copyright 2017 CerebroData Inc.
#

from __future__ import absolute_import

import builtins
import warnings
import logging
import string
import random
import six
from logging import NullHandler

def get_logger_and_init_null(logger_name):
    logger = logging.getLogger(logger_name)
    logger.addHandler(NullHandler())
    return logger


log = get_logger_and_init_null(__name__)


def _random_id(prefix='', length=8):
    return prefix + ''.join(random.sample(string.ascii_uppercase, length))

def to_bytes(text):
    if isinstance(text, builtins.bytes):
        # We already have bytes, so do nothing
        return text
    if isinstance(text, list):
        # Convert a list of integers to bytes
        return builtins.bytes(text)
    else:
        # Convert UTF-8 text to bytes
        return builtins.bytes(str(text), encoding='utf-8')

def _escape(s):
    e = s
    e = e.replace('\\', '\\\\')
    e = e.replace('\n', '\\n')
    e = e.replace('\r', '\\r')
    e = e.replace("'", "\\'")
    e = e.replace('"', '\\"')
    log.debug('%s => %s', s, e)
    return e


def _py_to_sql_string(value):
    if value is None:
        return 'NULL'
    elif isinstance(value, six.string_types):
        return "'" + _escape(value) + "'"
    else:
        return str(value)


# Logging-related utils


def warn_deprecate(functionality='This', alternative=None):
    msg = ("{0} functionality in pycerebro is now deprecated and will be removed "
           "in a future release".format(functionality))
    if alternative:
        msg += "; Please use {0} instead.".format(alternative)
    warnings.warn(msg, Warning)
