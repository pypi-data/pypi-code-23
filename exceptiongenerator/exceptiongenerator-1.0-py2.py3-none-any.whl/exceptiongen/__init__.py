#!/usr/bin/env python
# -*- coding: utf-8 -*-


def exception_generator(name, obj, message=''):
    def __init__(self):
        Exception.__init__(self, message)
    name = type(name, (obj,), {'__init__': __init__})
    return name
