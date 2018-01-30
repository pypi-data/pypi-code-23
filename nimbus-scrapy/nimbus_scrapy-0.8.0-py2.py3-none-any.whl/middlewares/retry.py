# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import logging
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

try:
    from urllib2 import _parse_proxy
except ImportError:
    from urllib.request import _parse_proxy
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware as SRetryMiddleware


class RetryProxyMiddleware(SRetryMiddleware):
    EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                  ConnectionRefusedError, ConnectionDone, ConnectError,
                  ConnectionLost, TCPTimedOutError, ResponseFailed,
                  IOError, TunnelError)
    custorm_proxys = {}
    retry_http_codes = set()

    def __init__(self, settings=None):
        super(RetryProxyMiddleware, self).__init__(settings)
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            spider.log(u"http proxy process request: {}".format(request.meta))

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        spider.log(u"http proxy process response")
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry_change_proxy(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        spider.log(u"http proxy process exception: {}".format(exception))
        if isinstance(exception, self.EXCEPTIONS) and not request.meta.get('dont_retry', False):
            return self._retry_change_proxy(request, exception, spider)

    def _retry_change_proxy(self, request, reason, spider):
        pop_proxy = getattr(spider, "pop_proxy", None)
        proxy = None
        if property and callable(pop_proxy):
            proxy = pop_proxy()
            if proxy and isinstance(proxy, (list, tuple)) and len(proxy) >= 1:
                proxy = proxy[1]
        spider.log(u"proxy: {}".format(proxy))
        if proxy:
            request.meta['proxy'] = proxy


