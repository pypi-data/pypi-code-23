"""Template registry behavior and base classes"""

from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import jinja2


# pylint: disable=too-many-instance-attributes
# 8 instance attributes is appropriate in this case

class Registry(object):
    """Template registry"""

    def __init__(self):
        """Set up namespace and template registries"""
        self.namespaces = {}
        self.global_defaults = {}
        self.namespace_defaults = collections.defaultdict(dict)
        self._environment_options = {}
        self._environment_filters = {}
        self._environment = None

    @property
    def environment_filters(self):
        """Dictionary containing jinja2 environment filters"""
        filters = dict(self._environment_filters)
        return filters

    @environment_filters.setter
    def environment_filters(self, value):
        self._environment_filters = value
        del self.environment

    @property
    def environment_options(self):
        """Dictionary containing Jinja2 environment config"""
        envopts = dict(self._environment_options)
        loader = jinja2.PrefixLoader(self.namespaces)
        envopts['loader'] = loader
        return envopts

    @environment_options.setter
    def environment_options(self, value):
        self._environment_options = value
        del self._environment

    @property
    def environment(self):
        """The Jinja2 environment"""
        if getattr(self, '_environment', None) is None:
            self._environment = jinja2.Environment(**self.environment_options)
            self._environment.filters.update(self.environment_filters)
        return self._environment

    @environment.deleter
    def environment(self):
        self._environment = None

    def register_namespace(self, namespace, loader, defaults):
        """Register a new loader"""
        if defaults is not None:
            self.namespace_defaults[namespace] = defaults
        self.namespaces[namespace] = loader
        del self.environment

    def set_defaults(self, renderer):
        """Update renderer with defaults appropriate to its template"""
        if renderer.namespace:
            defaults = self.namespace_defaults[renderer.namespace]
            for key in defaults:
                renderer.setdefault(key, defaults[key])
        for key in self.global_defaults:
            renderer.setdefault(key, self.global_defaults[key])

    def render(self, renderer):
        """Render the template to HTML"""
        template = self.environment.get_template(renderer.template)
        return template.render(**renderer)

REGISTRY = Registry()


class Renderer(dict):
    """Template renderer base class"""

    registry = REGISTRY
    namespace = None
    defaults = {}

    def __init__(self, template, namespace=None, registry=None):
        """Store the appropriate Jinja2 template and potentially
        override the namespace of the class.
        """
        super(Renderer, self).__init__(self.defaults)
        if namespace:
            self.namespace = namespace
        if registry:
            self.registry = registry
        self.template = template
        self.registry.set_defaults(self)

    def render(self):
        """Render the template to HTML"""
        return self.registry.render(self)


def register_loader(namespace, loader, defaults=None, registry=None):
    """Set up a namespace with a Jinja2 template loader"""
    if registry is None:
        registry = REGISTRY
    registry.register_namespace(
        namespace, loader, defaults,
    )


def register_filesystem_loader(namespace, path, *args, **kwargs):
    """Set up a namespace with a Jinja2 FileSystemLoader"""
    loader = jinja2.FileSystemLoader(path)
    return register_loader(namespace, loader, *args, **kwargs)


def set_environment_options(options, registry=None):
    """Set the environment options for the default registry"""
    if registry is None:
        registry = REGISTRY
    registry.environment_options = options


def set_global_defaults(defaults, registry=None):
    """Set the global defaults for all renderers in the default registry"""
    if registry is None:
        registry = REGISTRY
    registry.global_defaults = dict(defaults)


def set_environment_filters(filters, registry=None):
    """Set an environment filter for use in the templates"""
    if registry is None:
        registry = REGISTRY
    registry.environment_filters = filters
