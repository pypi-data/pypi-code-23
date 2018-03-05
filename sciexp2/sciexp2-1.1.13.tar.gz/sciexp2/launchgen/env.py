#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions typically used with `~sciexp2.launchgen`:

- `~sciexp2.launchgen.Launchgen`
- `~sciexp2.launchgen.defer`
- `~sciexp2.launchgen.file_contents`
- `~sciexp2.common.filter.Filter`
- ``v_``, an instance of `~sciexp2.common.filter.PFilter`

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


def _env_setup():
    import sciexp2.launchgen
    import sciexp2.common.filter

    _env_add("Launchgen", sciexp2.launchgen.Launchgen)
    _env_add("file_contents", sciexp2.launchgen.file_contents)
    _env_add("defer", sciexp2.launchgen.defer)
    _env_add("Filter", sciexp2.common.filter.Filter)
    _env_add("v_", sciexp2.common.filter.PFilter())

_env_setup()
