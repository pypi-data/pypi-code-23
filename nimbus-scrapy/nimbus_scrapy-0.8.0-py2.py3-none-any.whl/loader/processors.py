# -*- coding: utf-8 -*-
from __future__ import absolute_import
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.datatypes import MergeDict
from scrapy.loader.common import wrap_loader_context


class MapComposeDefault(object):

    def __init__(self, *functions,  **default_loader_context):
        self.default = default_loader_context.pop('default', None)
        self.functions = functions
        self.default_loader_context = default_loader_context

    def __call__(self, value, loader_context=None):
        values = arg_to_iter(value)
        if loader_context:
            context = MergeDict(loader_context, self.default_loader_context)
        else:
            context = self.default_loader_context
        wrapped_funcs = [wrap_loader_context(f, context) for f in self.functions]
        for func in wrapped_funcs:
            next_values = []
            for v in values:
                next_values += arg_to_iter(func(v))
            values = next_values
        return values or arg_to_iter(self.default)


class TakeFirstDefault(object):

    def __init__(self, default=""):
        self.default = default

    def __call__(self, values):
        for value in values:
            if value is not None and value != '':
                return value
        return self.default





