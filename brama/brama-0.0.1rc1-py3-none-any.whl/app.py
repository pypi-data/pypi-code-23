import importlib
import ujson

from sanic import Sanic

from . import default_config
from . import registry
from .api import API
from .route import Route
from .utils import pathjoin, unique_items, yaml_config_parse

BRAMA_PREFIX = 'BRAMA_'


class Brama(Sanic):
    def __init__(self, *args, **kwargs):
        self.api_registry = kwargs.pop('api_registry',
                                       registry.api_registry)
        self.plugins_registry = kwargs.pop('plugins_registry',
                                           registry.plugins_registry)

        if self.api_registry:
            self.api_registry.init_app(self)

        if self.plugins_registry:
            self.plugins_registry.init_app(self)

        self.api_base_path = kwargs.pop('api_base_path', '/')
        self.api_route_class = kwargs.pop('api_route_class', Route)
        self.global_plugins = kwargs.pop('global_plugins', [])

        super(Brama, self).__init__(*args, **kwargs)

        self.config.from_object(default_config)
        self.config.load_environment_vars(BRAMA_PREFIX)

    def register_route(self, route_, api=None, namespace_path=None):
        if isinstance(route_, dict):
            route = self.api_route_class(api, **route_)
        else:
            route = route_

        if namespace_path:
            prefix_path = pathjoin(self.api_base_path, namespace_path)
        else:
            prefix_path = self.api_base_path
        listen_path = pathjoin(prefix_path, route.url_path)

        self.route(
            uri=listen_path,
            methods=route.methods,
            stream=route.stream,
            name=route.name)(route.route_handler_factory(prefix_path))
        return route_

    def register_api(self, obj_or_class):
        if isinstance(obj_or_class, type):
            api = obj_or_class()
        else:
            api = obj_or_class

        if api.active:
            # Deactivated API basically means it's unreachable because not
            # registered in router.
            for route_ in api.routes:
                self.register_route(route_, api=api, namespace_path=api.name)

        self.api_registry.add(api.name, api)
        return obj_or_class

    def load_plugins(self, path_=None):
        path_ = path_ or ''
        pathes = path_.split(',')
        pathes.extend(self.config.get('PLUGINS_MODULES', []))
        pathes.insert(0, 'brama.contrib.plugins')

        for path in [x for x in pathes if x]:
            importlib.import_module(path)

        # Use plugins that provides routes
        for route_plugin in self.enabled_plugins(
                required_methods=['get_extra_routes']):
            [self.register_route(r)
             for r in route_plugin.get_extra_routes(self)]

    def load_config(self, path_or_dict):
        '''
        Known top-level keys of config object are parsed and added to the app.
        Unknown keys are ignored.
        :param path_or_dict: Path to config file or dict
        '''
        if isinstance(path_or_dict, str):
            path = path_or_dict
            if path.endswith('.json'):
                with open(path, 'r') as config_file:
                    config = ujson.load(config_file)
            elif path.endswith('.yaml') or path.endswith('.yml'):
                with open(path, 'r') as config_file:
                    config = yaml_config_parse(config_file)
            else:
                raise ValueError("Unknown config file format")
        else:
            config = dict(path_or_dict)

        self.config.update(config.get('settings', {}))
        self.global_plugins.extend(config.get('global_plugins', []))

        for api_name, api_conf in config.get('apis', []).items():
            api = API(name=api_name, **api_conf)
            self.register_api(api)

    def enabled_plugins(self, api=None, route=None, required_methods=(),
                        types=None):
        '''
        Returns plugins iterator with global enabled plugins, plus
        api and route specific, if those parameters provided.
        :param api: consider enabled if listed in provided api
        :param route: consider enabled if listed in provided route
        :param required_methods: exclude plugins that don't have this methods
        :param types: exclude plugins that has different type
        :return: iterator
        '''
        required_methods = set(required_methods)
        enabled_plugins = list()

        # Form a set if plugins with respect to priority
        enabled_plugins.extend(self.global_plugins)
        if route:
            enabled_plugins.extend(route.plugins)
        if api is not None:
            enabled_plugins.extend(api.plugins)

        for plugin_ in unique_items(enabled_plugins):
            if not isinstance(plugin_, str):
                plugin = plugin_
            else:
                plugin = self.plugins_registry.get(plugin_)
                if not plugin:
                    raise ValueError(
                        'Plugin {} can not be loaded'.format(plugin_))

            if types and plugin.type not in types:
                continue

            # Help plugins to let user know which config vars are required
            # and missing.
            _conf_err = (
                '{} config is required for plugin {}. '
                'You can set it via environment variable named {}'
            )
            if plugin.required_config:
                for _var_name in plugin.required_config:
                    _var_name = _var_name.upper()

                    if _var_name not in self.config.keys():
                        err = _conf_err.format(
                            _var_name, plugin.name,
                            "%s%s" % (BRAMA_PREFIX, _var_name)
                        )
                        raise ValueError(err)

            if required_methods.issubset(set(dir(plugin))):
                yield plugin
