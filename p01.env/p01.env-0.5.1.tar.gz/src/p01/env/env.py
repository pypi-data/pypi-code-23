##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Environment setup helper methods
$Id: env.py 4725 2018-02-04 12:21:29Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import os.path

_marker = object()

TRUE_VALUES = ['1', 'true', 'True', 'ok', 'yes', True]
FALSE_VALUES = ['0', 'false', 'False', 'no', False]


def makeBool(value, envKey):
    if value in TRUE_VALUES:
        return True
    elif value in FALSE_VALUES:
        return False
    else:
        tv = ', '.join([str(v) for v in TRUE_VALUES])
        fv = ', '.join([str(v) for v in FALSE_VALUES])
        # raise error if None, unknown value or empty value is given
        raise ValueError(
            "p01.env requires \"%s\" or \"%s\" as \"%s\" boolean value and "
            "not: \"%s\"" % (tv, fv, envKey, value))


def doConvert(func, envKey, value):
    """Convert and return value with given convertion function or show error"""
    try:
        return func(value)
    except Exception as e:
        raise ValueError("p01.env key \"%s\" convertion failed for value "
            "\"%s\" with error: \"%s\"" % (envKey, value, e))


def getEnviron(envKey, required=False, rType=unicode, default=_marker):
    """Get environment value for given key"""
    if default is _marker:
        default = None
    value = os.environ.get(envKey, _marker)
    if value is _marker:
        # no value, handle marker or missing
        if required:
            raise ValueError(
                "p01.env requires \"%s\" in your os.environ" % (envKey))
        else:
            return default
    else:
        # value given, convert
        if rType is bool:
            return makeBool(value, envKey)
        elif rType == 'path':
            return os.path.abspath(value)
        else:
            # use given callable, can use makeBool or custom converter
            return doConvert(rType, envKey, value)
