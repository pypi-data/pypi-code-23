#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Errors raised during data extraction."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


class EmptyFileError (Exception):
    """File was unexpectedly empty."""

    def __init__(self, path):
        self.path = path

    def __str__(self):
        if self.path is None:
            return ""
        else:
            return self.path


class ExtractError (Exception):
    """Error extracting from file."""

    def __init__(self, path, exception):
        self.path = path
        self.exception = exception

    def __str__(self):
        msg = "Unexpected error while extracting source %s" % self.path
        msg += "\n  [was] "
        msg += "%s: %s" % (self.exception.__class__.__name__,
                           str(self.exception))
        return msg


class ProbeError (Exception):
    """Error probing from file."""

    def __init__(self, path, exception):
        self.path = path
        self.exception = exception

    def __str__(self):
        path = " %s" % self.path if self.path is not None else ""
        msg = "Unexpected error while probing source%s" % path
        msg += "\n  [was] "
        msg += "%s: %s" % (self.exception.__class__.__name__,
                           str(self.exception))
        return msg


__all__ = [
    "EmptyFileError", "ExtractError", "ProbeError",
]
