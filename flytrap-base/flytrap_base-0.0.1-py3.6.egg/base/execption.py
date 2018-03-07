#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap


class FlytrapException(Exception):
    message = ''


class UserExistException(FlytrapException):
    message = "user is exist"
