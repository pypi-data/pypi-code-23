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
$Id: env.py 4705 2018-01-28 23:49:43Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import os.path

_marker = object()

TRUE_VALUES = ['1', 'true', 'True', 'ok', 'yes', True]
FALSE_VALUES = ['0', 'false', 'False', 'no', False]


def makeBool(value):
    if value in TRUE_VALUES:
        return True
    elif value in FALSE_VALUES:
        return False
    else:
        # raise error if None, unknown value or empty value is given
        raise ValueError("Must use a known bool string and not %s" %
            type(value), value)


def getEnviron(envKey, required=False, rType=unicode, default=_marker):
    """Get environment value for given key"""
    if default is _marker:
        default = None
    value = os.environ.get(envKey, _marker)
    if value is _marker:
        # no value, handle marker or missing
        if required:
            raise ValueError(
                "You must define \"%s\" for run this server" % (envKey))
        else:
            return default
    else:
        # value given, convert
        if rType is bool:
            return makeBool(value)
        elif rType == 'path':
            return os.path.abspath(value)
        else:
            # can use makeBool
            return rType(value)
