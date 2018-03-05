#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Relevant functions and objects to work with `~sciexp2.data`.

Provides all "public" contents of the following modules:

* `sciexp2.data`
* `sciexp2.data.io`
* `sciexp2.data.meta`

Also provides `~sciexp2.common.filter.Filter` and an instance of
`~sciexp2.common.filter.PFilter` named `v_` to help streamlining the writing of
filters.

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


__all__ = []


def _env_add(name, value):
    __all__.append(name)
    globals()[name] = value


def _env_add_all(module):
    for i in module.__all__:
        _env_add(i, getattr(module, i))


def _env_setup():
    import sciexp2.data
    import sciexp2.data.meta
    import sciexp2.data.io
    import sciexp2.common.filter
    _env_add_all(sciexp2.data)
    _env_add_all(sciexp2.data.meta)
    _env_add_all(sciexp2.data.io)
    _env_add("Filter", sciexp2.common.filter.Filter)
    _env_add("v_", sciexp2.common.filter.PFilter())

_env_setup()
