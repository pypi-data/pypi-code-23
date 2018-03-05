#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simplified pretty-printing."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2011-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import IPython.lib.pretty


class Pretty (object):
    """Provide repr/str through IPython's `pretty` module.

    Child classes must implement the `_repr_pretty_` method.

    """

    def pformat(self, p, cycle, name=None):
        """Return pretty representation.

        Automatically handles cycles and adds a proper group with the class
        name.

        This is designed to be used on a *with* statement.

        """
        if name is None:
            name = self.__class__.__name__

        if cycle:
            p.text("%s(...)" % name)
        else:
            begin = "%s(" % name
            return p.group(len(begin), begin, ")")

    def __repr__(self):
        return IPython.lib.pretty.pretty(self)
