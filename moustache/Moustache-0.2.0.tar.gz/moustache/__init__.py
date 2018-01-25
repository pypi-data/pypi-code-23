#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module de fusion documentaire
"""
__version__ = "0.2.0"


def launch():
    from moustache import wssecretary
    wssecretary.default_app().run(debug=True, host='0.0.0.0')
