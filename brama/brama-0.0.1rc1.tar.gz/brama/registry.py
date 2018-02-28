from .utils import Registry


class ApiRegistry(Registry):

    def add(self, api_name, api):
        self.add_item(api_name, api)

    def get(self, api_name):
        return self.get_item(api_name)


class PluginsRegistry(Registry):

    def add(self, plugin):
        self.add_item(plugin.name, plugin)

    def get(self, name, type_=None):
        plugin = self.get_item(name)
        if plugin and type_ and plugin.type != type_:
            raise TypeError('Plugin with name {} is not of type {}'.format(
                name, type_
            ))
        return plugin


api_registry = ApiRegistry()
plugins_registry = PluginsRegistry()
