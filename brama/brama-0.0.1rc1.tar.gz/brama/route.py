from .handlers import ProxyHandler, LocalHandler


class Route(object):
    def __init__(self, api=None, name=None, url_path=None, strip_path=False,
                 upstreams=None, handler=None, methods=None, plugins=None,
                 stream=False, **kwargs):
        self.api = api
        self.url_path = url_path
        self.name = name
        self.strip_path = strip_path
        self.upstreams = upstreams
        self.handler = handler
        self.stream = stream
        self.methods = methods if methods else {'GET'}
        self.plugins = plugins if plugins else []

        self._extra_config = {}

        for k, v in kwargs.items():
            self._extra_config[k] = v

        if not self.url_path:
            raise ValueError('url_path is required')

        if self.upstreams and self.handler:
            raise ValueError('Only one of upstreams or handler could be used')
        if not self.upstreams and not self.handler:
            raise ValueError('One of upstreams or handler should be set')

    @property
    def is_proxy(self):
        return True if self.upstreams else False

    def route_handler_factory(self, prefix_path):
        if self.is_proxy:
            kls = ProxyHandler
        else:
            kls = LocalHandler
        return kls(self, prefix_path)

    def get_config(self, param_name):
        route_value = self._extra_config.get(param_name, None)
        api_value = self.api.get_config(param_name) if self.api else None

        if isinstance(route_value, str) or isinstance(api_value,
                                                      str):
            return route_value or api_value

        if isinstance(route_value, list) or isinstance(api_value, list):
            return route_value or api_value

        if isinstance(route_value, dict) or isinstance(api_value, dict):
            _res_dict = {}
            _res_dict.update(api_value) if api_value is not None else None
            _res_dict.update(route_value) if route_value is not None else None
            return _res_dict
