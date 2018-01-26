# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Django hook strategy
"""

from logging import getLogger

from ..middlewares import DjangoMiddleware
from .framework import FrameworkStrategy

LOGGER = getLogger(__name__)


def load_middleware_insert(original, middleware):
    import django

    def wrapped_load_middleware(self, *args, **kwargs):
        LOGGER.debug("Execute load_middleware_insert")

        # Load original middlewares.
        result = original(self, *args, **kwargs)

        if django.VERSION < (2, 0):
            insert_middleware_v1(self)
        else:
            insert_middleware_v2(self)

        return result

    def insert_middleware_v1(self):
        LOGGER.debug("Insert old-style Django middleware")

        # Insert Sqreen middleware.
        try:
            self._view_middleware.insert(0, middleware.process_view)
            self._response_middleware.append(middleware.process_response)
            self._exception_middleware.append(middleware.process_exception)
        except Exception:
            LOGGER.warning("Error while inserting our middleware",
                           exc_info=True)

    def insert_middleware_v2(self):
        LOGGER.debug("Insert new-style Django middleware")

        # Retrieve the original middleware chain.
        orig_mw_chain = self._middleware_chain

        # New middleware chain, including Sqreen. This function processes
        # responses, so Sqreen middleware is the last one.
        def mw_chain(request):
            response = orig_mw_chain(request)
            response = middleware.process_response(request, response)
            return response

        # Insert Sqreen middleware.
        try:
            self._view_middleware.insert(0, middleware.process_view)
            self._exception_middleware.append(middleware.process_exception)
            self._middleware_chain = mw_chain
        except Exception:
            LOGGER.warning("Error while inserting our middleware",
                           exc_info=True)

    return wrapped_load_middleware


class DjangoStrategy(FrameworkStrategy):
    """ Strategy for Django peripheric callbacks.

    It injects a custom DjangoFramework that calls callbacks for each
    lifecycle method
    """

    MODULE_NAME = "django.core.handlers.base"
    HOOK_CLASS = "BaseHandler"
    HOOK_METHOD = "load_middleware"

    def __init__(self, strategy_key, observation_queue, queue, import_hook, before_hook_point=None):
        super(DjangoStrategy, self).__init__(strategy_key, observation_queue, queue, import_hook, before_hook_point)

        self.middleware = DjangoMiddleware(self, observation_queue, queue)
        self.wrapper = load_middleware_insert
