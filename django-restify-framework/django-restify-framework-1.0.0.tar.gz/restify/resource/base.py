import six
import logging
from functools import update_wrapper

from django import http
from django.http.response import HttpResponseBase
from django.utils.decorators import classonlymethod

from restify import serializers
from restify.http import status
from restify.http.response import ApiResponse

logger = logging.getLogger('django.request')


class ResourceOptions:
    resource_name = None
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head']
    serializer = serializers.BaseSerializer
    authentication = None
    authorization = None


class ResourceMeta(type):
    options_class = ResourceOptions

    def __new__(cls, name, bases, attrs):
        new = super(ResourceMeta, cls).__new__(cls, name, bases, attrs)
        meta = attrs.pop('Meta', cls.options_class)
        for attr in dir(cls.options_class):
            if not attr.startswith('__') and not hasattr(meta, attr):
                setattr(meta, attr, getattr(cls.options_class, attr))
        setattr(new, '_meta', meta)
        return new


class Resource(object, metaclass=ResourceMeta):
    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @property
    def serializer(self):
        return self._meta.serializer

    @property
    def resource_name(self):
        return self._meta.resource_name

    @property
    def authentication(self):
        return self._meta.authentication

    @property
    def authorization(self):
        return self._meta.authorization

    @classonlymethod
    def as_callable(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    def __call__(self, request, *args, **kwargs):
        """
        Steps:
            1. Dispatch to the right method (don't call it!!!)
            2. Preprocess the request: This method can set class instance wide attributes (select object from database etc...)
               If it raises error, the HTTP 400 response is generated.
            3. Run dispatched method
            4. If method returns HttpResponse the return, else serialize retval
            5. Return HttpResponse with serialized data (only json at this time)
        """
        method = self.dispatch(request, *args, **kwargs)
        if method == self.http_method_not_allowed:
            return method(request, *args, **kwargs)

        if self.authentication is not None:
            auth = self.authentication()
            if not auth.is_authenticated(request=request):
                return auth.unauthorized()

        if self.authorization is not None:
            if getattr(request, 'user', None) is None:
                return self.authorization.unauthorized()

            if not self.authorization.has_perm(request.user, http_method=request.method.lower()):
                return self.authorization.unauthorized()

        resp = self.common(request, *args, **kwargs)
        if isinstance(resp, HttpResponseBase):
            return resp
        resp = method(request, *args, **kwargs)
        if isinstance(resp, HttpResponseBase):
            return resp
        return resp.to_django_response(serializer=self.serializer)

    def common(self, request, *args, **kwargs):
        """
        Preprocess the request, before run "view" method (get, post, etc...).

        :param request: Django HttpRequest object
        :return: None
        """
        return

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self._meta.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
                       extra={
                           'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
                           'request': request
                       })
        return http.HttpResponseNotAllowed(self._allowed_methods())

    def _allowed_methods(self):
        return [m.upper() for m in self._meta.http_method_names if hasattr(self, m)]
