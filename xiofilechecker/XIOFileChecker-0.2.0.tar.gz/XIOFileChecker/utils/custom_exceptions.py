#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Custom exceptions used in this module.

"""


class ExpressionNotMatch(Exception):
    """
    Raised when a regular expression resolution failed.

    """

    def __init__(self, string, pattern):
        self.msg = "Pattern resolution failed"
        self.msg += "\n<value: '{}'>".format(string)
        self.msg += "\n<pattern: '{}'>".format(pattern)
        super(self.__class__, self).__init__(self.msg)


class InvalidFilters(Exception):
    """
    Raised when a regular expression resolution failed.

    """

    def __init__(self, filters, facets):
        self.msg = "Invalid filter(s)"
        self.msg += "\n<unrecognized_filters: '{}'>".format(', '.join(filters))
        self.msg += "\n<available_filters: '{}'>".format(', '.join(facets))
        super(self.__class__, self).__init__(self.msg)


class NoFileFound(Exception):
    """
    Raised when no netCDF files have been found.

    """

    def __init__(self):
        self.msg = "No netCDF files found."
        super(self.__class__, self).__init__(self.msg)


class NoPatternFound(Exception):
    """
    Raised when no file patterns found in filedef.

    """

    def __init__(self):
        self.msg = "No file patterns found"
        super(self.__class__, self).__init__(self.msg)