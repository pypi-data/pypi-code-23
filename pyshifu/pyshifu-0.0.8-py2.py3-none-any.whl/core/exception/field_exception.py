#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals
from pyshifu.core.exception.base_exception import ShifuException
from pyshifu.core.enums import ErrorNo


class FieldException(ShifuException):
    def get_error_no(self):
        return ErrorNo.FIELD_INVALID

    def get_description(self):
        return "Field value invalid!"
