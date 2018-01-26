# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Record request context."""

from logging import getLogger

from ..frameworks.aiohttp_framework import AioHTTPRequest
from .record_request_context import RecordRequestContext

LOGGER = getLogger(__name__)


class RecordRequestContextAioHTTP(RecordRequestContext):
    """Record request context."""

    def pre(self, original, request):
        self._store_request(AioHTTPRequest(request))

    def post(self, *args, **kwargs):
        self._clear_request()

    def failing(self, *args, **kwargs):
        self._clear_request()
