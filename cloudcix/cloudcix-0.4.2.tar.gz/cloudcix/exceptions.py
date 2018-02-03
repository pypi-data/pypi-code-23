# -*- coding: utf-8 -*-

"""
cloudcix.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of custom exceptions for cloudcix
"""


class ImproperlyConfigured(Exception):
    """cloudcix is missing a setting or settings module"""
    pass


class MissingClientKwarg(Exception):
    """A required kwarg is missing from the client request call"""

    def __init__(self, name, cli):
        self.name = name
        self.message = "{} argument is required by the {}".format(
            name, cli
        )

    def __str__(self):
        return self.message

    def __repr__(self):
        return "<MissingClientKwarg [{}]>".format(self.name)