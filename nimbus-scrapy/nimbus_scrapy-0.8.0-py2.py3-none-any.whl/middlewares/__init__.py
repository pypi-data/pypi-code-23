# -*- coding: utf-8 -*-
from __future__ import absolute_import
from scrapy.exceptions import NotConfigured


class NimbusMiddleware(object):

    def __init__(self, settings=None):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        process = getattr(spider, "process_request", None)
        if process and callable(process):
            return process(request, spider)

    def process_response(self, request, response, spider):
        process = getattr(spider, "process_response", None)
        if process and callable(process):
            return process(request, response, spider)
        return response

    def process_exception(self, request, exception, spider):
        process = getattr(spider, "process_exception", None)
        if process and callable(process):
            return process(request, exception, spider)

