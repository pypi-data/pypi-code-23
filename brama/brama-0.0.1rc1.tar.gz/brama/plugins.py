from . import registry


class Plugin(object):
    type = None
    _required_config = []
    _wrapped_object = None

    def __init__(self, name, required_config=None):
        self.name = name
        if required_config:
            self._required_config = required_config

    @classmethod
    def register(cls, plugin_name=None, *args, **kwargs):
        def wrapper(obj):
            name = plugin_name if plugin_name else obj.__name__
            plugin = cls.register_new(name, *args, **kwargs)
            plugin.wrapped_object = obj
            plugin.required_config = kwargs.get('required_config', [])
            registry.plugins_registry.add(plugin)
            return obj

        return wrapper

    @classmethod
    def register_new(cls, name, *args, **kwargs):
        return cls(name, *args, **kwargs)

    @property
    def wrapped_object(self):
        return self._wrapped_object

    @wrapped_object.setter
    def wrapped_object(self, obj):
        self._wrapped_object = obj


class RouteHandlerPlugin(Plugin):
    type = 'route_handler'


class RoutesPlugin(Plugin):
    type = 'routes'

    def get_extra_routes(self, app):
        return self.wrapped_object(app) or []


class AuthorizationFlowPlugin(Plugin):
    type = 'authorization_flow'

    def process_login(self, request, username, password):
        obj = self.wrapped_object()
        if not hasattr(obj, 'process_login'):
            raise NotImplementedError()
        return obj.process_login(request, username, password)

    def get_extra_routes(self, app):
        '''
        Allow Authorization plugins to define routes.
        :return: list
        '''
        obj = self.wrapped_object()
        if not hasattr(obj, 'get_extra_routes'):
            return []
        return obj.get_extra_routes(app)


class AuthorizationPlugin(Plugin):
    type = 'authorization'

    def get_authorization_value(self, request):
        obj = self.wrapped_object()
        if not hasattr(obj, 'get_authorization_value'):
            raise NotImplementedError()
        return obj.get_authorization_value(request)

    def process_authorization_value(self, app, value):
        obj = self.wrapped_object()
        if not hasattr(obj, 'process_authorization_value'):
            raise NotImplementedError()
        return obj.process_authorization_value(app, value)


class MiddlewarePlugin(Plugin):
    type = 'middleware'
    attached_to = 'request'

    def __init__(self, name, attached_to=None):
        if attached_to is not None:
            self.attached_to = attached_to
        super(MiddlewarePlugin, self).__init__(name)

    @classmethod
    def register_new(cls, name, *args, **kwargs):
        attached_to = kwargs.get('attached_to', 'request')
        return cls(name, attached_to)

    def process_request(self, *args, **kwargs):
        if self.attached_to == 'request':
            return self.wrapped_object(*args, **kwargs)

    def process_response(self, *args, **kwargs):
        if self.attached_to == 'response':
            return self.wrapped_object(*args, **kwargs)


class RequestTransformPlugin(MiddlewarePlugin):
    type = 'request_transformation'
    attached_to = 'request'

    @classmethod
    def register_new(cls, name, *args, **kwargs):
        return cls(name)


class ResponseTransformPlugin(MiddlewarePlugin):
    type = 'response_transformation'
    attached_to = 'response'

    @classmethod
    def register_new(cls, name, *args, **kwargs):
        return cls(name)
