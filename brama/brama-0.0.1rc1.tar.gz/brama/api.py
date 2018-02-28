class API(object):
    name = None
    verbose_name = None
    active = True
    routes = []
    plugins = []
    _extra_config = {}

    def __init__(self, name=None, verbose_name=None, routes=None, plugins=None,
                 active=None, **kwargs):
        if name:
            self.name = name
        if verbose_name:
            self.verbose_name = verbose_name
        if routes is not None:
            self.routes = routes
        if plugins is not None:
            self.plugins = plugins
        if active is not None:
            self.active = active

        self._extra_config = {}
        for k, v in kwargs.items():
            self._extra_config[k] = v

    def get_config(self, param_name):
        return self._extra_config.get(param_name, None)
