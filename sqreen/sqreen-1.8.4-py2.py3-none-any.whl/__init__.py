# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Sqreen python agent package
"""
from .__about__ import __author__, __email__, __version__
from .runner_thread import start
from .sdk.auth import auth_track, identify, signup_track


__all__ = [
    '__author__',
    '__email__',
    '__version__',
    'start',
    'auth_track',
    'signup_track',
    'identify',
]
