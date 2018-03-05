#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Compatibility functions."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2016-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import inspect
import six
import sys


if sys.version_info < (3, 0):
    class InspectSignature(object):
        def __init__(self, func):
            self._func = func
            self._spec = inspect.getargspec(func)

        def __contains__(self, name):
            return name in self._spec.args

        def index(self, name):
            return self._spec.args.index(name)

    class InspectBind(object):
        def __init__(self, func, *args, **kwargs):
            self.args = []
            self.kwargs = inspect.getcallargs(func, *args, **kwargs)
            self.arguments = self.kwargs
else:
    class InspectSignature(object):
        def __init__(self, func):
            self._func = func
            self._sig = inspect.signature(func)

        def __contains__(self, name):
            return name in self._sig.parameters

        def index(self, name):
            return list(self._sig.parameters.keys()).index(name)

    class InspectBind(object):
        def __init__(self, func, *args, **kwargs):
            self._args = inspect.signature(func).bind(*args, **kwargs)
            self._args.apply_defaults()

        @property
        def args(self):
            return self._args.args

        @property
        def kwargs(self):
            return self._args.kwargs

        @property
        def arguments(self):
            return self._args.arguments


if sys.version_info < (3, 0):
    def StringIO(contents):
        return six.StringIO(contents)

else:
    def StringIO(contents):
        if isinstance(contents, str):
            contents = contents.encode('utf-8')
        return six.BytesIO(contents)
