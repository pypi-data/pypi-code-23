from collections import OrderedDict

from django.apps import apps
from django.conf.urls import url


class Api(object):
    """
    Implements a registry to tie together the various resources that make up
    an API.
    """

    def __init__(self, api_name="v1"):
        self.name = api_name
        self._registry = OrderedDict()
        self.app_name = apps.get_app_config('restify').name

    def register(self, regex, resource):
        """
        Registers an instance of a ``Resource`` subclass with the API.
        """
        if regex in self._registry.keys():
            raise ValueError("A new resource '%r' is replacing the existing URL on %s" % (resource, regex))

        self._registry[regex] = resource

    @property
    def urls(self):
        """
        Provides URLconf details for the ``Api`` and all registered
        ``Resources`` beneath it.
        """
        pattern_list = []  # TODO: add default urls eg. root, documentation

        for endpoint, resource in self._registry.items():
            pattern_list.append(url(endpoint, resource.as_callable(), name=resource._meta.resource_name))
        return pattern_list
