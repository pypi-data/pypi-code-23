#!/usr/bin/env python
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
#
"""Configuration options for template rendering and
parsing.

This class provides a compatibility bridge between customizable 
template backends and the Django ``RequestContext`` object.

TODO: Add support for Genshi templates.
"""
import os
from notmm.utils.template.interfaces import TemplateLoaderFactory
from notmm.utils.django_settings import SettingsProxy

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
cache_opts = {
    'cache.data_dir': '/tmp/cache/data',
    'cache.lock_dir': '/tmp/cache/lock',
    'cache.regions': 'short_term, long_term',
    'cache.short_term.type': 'ext:memcached',
    'cache.short_term.url': '127.0.0.1:11211',
    'cache.short_term.expire': '1200',
    'cache.long_term.type': 'ext:memcached',
    'cache.long_term.url' : '127.0.0.1:11211',
    'cache.long_term.expire': '86400'
}

__all__ = ('get_template_loader', 'get_app_conf')



class TemplateException(Exception):
    pass

def get_app_conf(name='development.ini'):

    try:
        from notmm.utils.configparse import loadconf
        rootdir = os.environ['ROOTDIR']
        app_conf = loadconf(name)
    except (ImportError, KeyError):
        app_conf = {}
    return app_conf

# register a default template backend instance 
def get_template_loader(cache_enabled=True):
    
    _settings = SettingsProxy(autoload=True).get_settings()
    _cache_enabled = getattr(_settings, 'ENABLE_BEAKER', cache_enabled)
    
    TemplateLoaderFactory.configure(
        #backend='mako', 
        #template_loader_class='CachedTemplateLoader',
        kwargs={
            'directories' : _settings.TEMPLATE_DIRS, 
            'cache_enabled':_cache_enabled,
            'cache_args': {
              'manager': CacheManager(**parse_cache_config_options(cache_opts))
              }
            }
    )
    loader = TemplateLoaderFactory.get_loader()
    return loader

