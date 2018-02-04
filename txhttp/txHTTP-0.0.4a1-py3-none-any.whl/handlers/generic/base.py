"""
Copyright: 2018, Yehuda Deutsch at Sync.me <yeh@uda.co.il>

Original work in Django is distributed under the BSD license (3-clause)

This handler is a port from Django's View class (django.views.generic.base.View)
"""
import logging
from functools import update_wrapper

from twisted.web.server import Request
from werkzeug.exceptions import MethodNotAllowed

from txhttp.utils.decorators import classonlymethod

logger = logging.getLogger(__name__)


class Handler:
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classonlymethod
    def as_handler(cls, **initkwargs):
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(f'You tried to pass in the {key} method name as a '
                                f'keyword argument to {cls.__name__}(). Don\'t do that.')
            if not hasattr(cls, key):
                raise TypeError(f'{cls.__name__}() received an invalid keyword {key}. as_handler '
                                'only accepts arguments that are already '
                                'attributes of the class.')

        def handler(*args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            # Pass klein bound instance to handler if available
            if not isinstance(args[0], Request):
                self.app = args[0]
                self.request = args[1]
                args = args[1:]
            else:
                self.app = None
                self.request = args[0]
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(*args, **kwargs)

        handler.handler_class = cls
        handler.handler_initkwargs = initkwargs

        # take name and docstring from class
        update_wrapper(handler, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(handler, cls.dispatch, assigned=())

        return handler

    def dispatch(self, request: Request, *args, **kwargs):
        """
        Try to dispatch to the right method; if a method doesn't exist,
        defer to the error handler. Also defer to the error handler if the
        request method isn't on the approved list.

        :param twisted.web.server.Request request:
        :param tuple args:
        :param dict kwargs:
        """
        if request.method.decode().lower() in self.http_method_names:
            handler = getattr(self, request.method.decode().lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        :param twisted.web.server.Request request:
        :param tuple args:
        :param dict kwargs:
        """
        logger.warning(
            f'Method Not Allowed ({request.method.decode()}): {request.path.decode()}',
            extra={'status_code': 405, 'request': request}
        )
        raise MethodNotAllowed(self._allowed_methods())

    def options(self, request, *args, **kwargs):
        """
        :param twisted.web.server.Request request:
        :param tuple args:
        :param dict kwargs:
        """
        request.setHeader(b'Allow', ', '.join(self._allowed_methods()).encode())
        request.setHeader(b'Content-Length', b'0')
        return b''

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class RedirectHandler(Handler):
    """Provide a redirect on any GET request."""
    permanent = False
    url = None

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        if self.url:
            url = self.url % kwargs
        else:
            return None

        return url

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if url:
            request.setHeader(b'location', url.encode())
            if self.permanent:
                request.setResponseCode(301)
            else:
                request.setResponseCode(302)
        else:
            logger.warning(
                f'Gone: {request.path.decode()}',
                extra={'status_code': 410, 'request': request}
            )
            request.setResponseCode(410)

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
