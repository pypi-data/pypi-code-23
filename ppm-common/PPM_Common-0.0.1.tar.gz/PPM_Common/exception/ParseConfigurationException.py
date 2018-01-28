# -*- coding: utf-8 -*-
"""
..  py:module:: ParseConfigurationException

This module contains ParseConfigurationException class
"""


class ParseConfigurationException(Exception):

    """
    Specific exception for parsing errors
    """

    def __init__(self, message):
        """
        Constructor
        :param message: for Exception class
        :type str
        """
        Exception.__init__(self, message)
