#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import sys
import traceback
from marshmallow import Schema, fields


class Error(Exception):
    def __init__(self, message, code=1, msgid=None, extra=None):
        Exception.__init__(self, code, message)
        self.message = message
        self.code = code
        self.msgid = msgid
        self.extra = extra or dict()
        self.stack = None

        exc_t, exc_v, exc_tb = sys.exc_info()
        if exc_t and exc_v and exc_tb:
            self.stack = "\n".join([
                x.rstrip() for x in traceback.format_exception(
                    exc_t, exc_v, exc_tb
                )
            ])

    def __repr__(self):
        return "%s<code=%s, message=%s>" % (
            self.__class__.__name__,
            self.code,
            self.message
        )

    def __str__(self):
        return "{}: {}".format(self.code, self.message)


class ErrorSchema(Schema):
    code = fields.Integer(required=True)
    message = fields.String(required=True)
    msgid = fields.String()
    extra = fields.Dict()
    stack = fields.String()
