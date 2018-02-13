#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# zeus: exception.py
#
# Define zeus exception handler
#
# Copyright (C) 2016-2017, Christophe Fauchard
# -----------------------------------------------------------------

"""
Submodule: zeus.exception

Zeus module specific exceptions definition

Copyright (C) 2016-2017, Christophe Fauchard
"""


class FileNotFoundException(Exception):

    def __init__(self, filename):
        self.filename = filename


class DirectoryNotFoundException(Exception):

    def __init__(self, directory):
        self.directory = directory


class InvalidConfigurationFileException(Exception):

    def __init__(self, filename):
        self.filename = filename


class PrivateKeyException(Exception):

    def __init__(self):
        pass
