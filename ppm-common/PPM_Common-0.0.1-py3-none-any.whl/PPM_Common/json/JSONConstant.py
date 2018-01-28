# -*- coding: utf-8 -*-
"""
..  py:module:: JSONConstant

This module contain JSONConstant class
"""


class JSONConstant(object):
    """
    ..  py:class:: JSONConstant()

    Declaration of constant fields in json configuration

    ..  note:: make it as a Enum. Items must be present in config file
    """

    # database data source
    MONGO = "mongodb"
    ELASTIC = "elastic"
    HOST = "host"
    PORT = "host_port"
    LOGIN = "user"
    PASSWORD = "pwd"
    MODE = "mode"
