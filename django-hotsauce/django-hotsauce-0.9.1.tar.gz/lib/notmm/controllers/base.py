#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2018 Etienne Robillard <tkadm30@yandex.ru>
# All rights reserved.
"""BaseController API Version 0.9.0

Python extension module to implement MVC-style "controllers"
for Django and WSGI type apps. In short, ``BaseController`` derived
extensions are request handlers resolving a ``path_url`` string
to a matching ``view function``. The response handler (view function)
then resolve the appropriate HTTP response to the client.

TODO:
-Better module-level documentation (work-in-progress)
-Compatibility with mod_wsgi (Apache2) (YMMV...)
-Change all prints by log() hooks (work-in-progress)
-use signals to log messages from pubsub like BUS

Define and document the internal request handling stages when
using native Django views (WSGIHandler):
 __init__,         # application init -> self.init_request(env)
 init_request,     # setup the environment -> self.process_request(req)
 process_request,  # handle the request -> self.locals.request = req
 get_response,     # resolve request [PATH_INFO] -> response_callback
 application,      # response stage 2 [WSGI] -> response_callback(env, start_response)
"""

import sys
import os
import urllib
import logging
import traceback

from gevent.local import local
from contextlib import contextmanager
from notmm.utils.wsgilib import (
    #HTTPClientError, 
    HTTPServerError, 
    HTTPRequest, 
    HTTPResponse,
    HTTPNotFound,
    HTTPUnauthorized
    #HTTPException
    )

from notmm.utils.django_compat import NoReverseMatch

from werkzeug.local import LocalProxy

RequestClass = HTTPRequest

_requests = local()


__all__ = ('BaseController', 'sessionmanager', 'get_current_request', 'request')


@contextmanager
def sessionmanager(environ):
    _requests.request = RequestClass(environ)
    yield
    _requests.request = None

def get_current_request():
    try:
        return _requests.request
    except AttributeError:
        raise TypeError("No request object for this thread")


request = LocalProxy(lambda: get_current_request())

class BaseController(object):
    
    def sethandle(self, name, string_or_callable):
        """Adds custom response handlers to a BaseController subclass.
        """

        # If string_or_callable is in the form of "foo.bar.quux",
        # the callable function should be the last part of the
        # string
        handler = None
        if isinstance(string_or_callable, str):
            if string_or_callable.find('.') != -1:
                bits = string_or_callable.rsplit('.', 1)
                m = __import__(bits[0], globals(), locals(), fromlist=[''])
                for component in bits[1:]:
                    if hasattr(m, component):
                        handler = getattr(m, component)
                        break
                    else:
                        #print 'debug: module %s has no such member: %r' % (m, component)
                        continue
        elif callable(string_or_callable):
            handler = string_or_callable
        else:
            raise ValueError("Unexpected string_or_callable type: %r" % \
                type(string_or_callable))

        if not callable(handler) and isinstance(handler, str):
            # Attempt to import it
            # XXX write a native eval_import hook
            if 'debug.config.eval_import_func' in self.app_conf:
                handler_obj = self.app_conf['debug.config.eval_import_func'](handler)
            else:
                raise Exception("fatal error: debug.config.eval_import_func not set!")
        else:
            handler_obj = handler

        # XXX Use staticmethod(func) here, because we want to support the
        # same positional arguments named by this callable
        setattr(self, name, handler_obj)

        return None

    def __call__(self, environ, start_response, exc_info=None):
        # WSGI 1.0 mandates to return a callable object
        #self._environ.update(environ)
        if exc_info is not None:
            # TODO: exc_info verifications
            if self.debug:
                self.logger.debug(exc_info)
            return self.application(environ, start_response, exc_info)
        return self.application(environ, start_response)

    def application(self, environ, start_response):
        """
        Override this to change the default request/response
        handling.

        This method is used for properly returning a WSGI response instance
        by calling ``get_response``.

        The latter does the grunt work of routing the request to the
        proper callable function or class.

        """
        self._environ = environ
        #self._request = self.init_request(self.environ)
        with sessionmanager(self.environ):
            self._request = self.init_request(request)
            self._request.environ.update(self.environ)
            if self.debug:
                assert self._request == get_current_request(), 'something is messed up!!!'
            response = self.get_response(request=self._request)
            return response(self._request.environ, start_response)

    def registerWSGIHandlers(self, d):
        """Register appropriate wsgi callbacks (legacy method
        for backward compat only)"""
        for k, v in d:
            # "register" the callback function as a standard Django view
            # accessible by the controller extension
            self.sethandle(k, v)
        #self.registered = True
        return None
    
    def init_request(self, request):
        """A method to execute before ``process_request``"""
        self._request = request
        return self._request    

    #request = property(init_request)

    def get_response(self, request, method='GET', data={}):
        """Process ``path_url`` and return a callable function as
        the WSGI ``response`` callback.

        The callback view function is resolved using the built-in
        Django ``RegexURLResolver`` class.

        Returns a callable function (Response) or None if no
        view functions matched.

        See the docs in :notmm.utils.django_compat.RegexURLResolver:
        for details.

        This function may be overrided in custom subclasses to modify
        the response type.
        """
        # Match the location to a view or callable
        #path_info = self.get_path_info(self.environ)

        try:
            if self.debug:
                #assert self.request != None, 'invalid request object!'
                self.logger.debug("Resolving path=%r"%request.path_url)

            # Resolve the path (endpoint) to a view using legacy Django URL
            # resolver.
            (callback, args, kwargs) = self.resolver.resolve(str(request.path_url))
            if self.debug and self.logger:
                self.logger.debug("callback resolved=%r"%callback)
            # Create the wsgi ``response`` object.
            response = callback(request, *args, **kwargs)
        except NoReverseMatch as e:
            # Handle 404 responses with a custom 404 handler.
            self.logger.info('Document not found=%s'%request.path_url)
            if self.debug:
                self.logger.debug(e)
            #handleclienterror(self.request)

            return self.handle404(request)
        except (HTTPServerError, Exception):

            exc = traceback.format_exc()

            if self.debug:
                self.logger.debug(exc)
                #assert isinstance(request, RequestClass) == True, type(request)

            return self.handle500(request)
        except (HTTPUnauthorized), exc:
            if self.debug:
                self.logger.debug("Caught authorization exception")
                self.logger.debug(exc)
            return self.handle401(request)
        else:
            #manager.clear()
            return response
    def _environ_getter(self):
        """ Returns the current WSGI environment instance."""
        return self._environ
    environ = property(_environ_getter)

    def _method_getter(self):
        return self.environ['REQUEST_METHOD']
    method = property(_method_getter)

    def _debug_getter(self):
        """Global debug flag. 
        Set settings.DEBUG to False to disable debugging"""
        return bool(self.settings.DEBUG == True)
    debug = property(_debug_getter)

    def _get_path_info(self, env):
        return str(env.get('PATH_INFO', ''))

