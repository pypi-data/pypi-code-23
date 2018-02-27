from importlib import import_module
from apollo.settings import apollo_settings


urls = import_module('apollo.api.%s.urls' % apollo_settings.API_VERSION)
serializers = import_module('apollo.api.%s.serializers' % apollo_settings.API_VERSION)