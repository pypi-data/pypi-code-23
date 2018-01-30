# -*- coding: utf-8 -*-

"""
cloudcix.conf
~~~~~~~~~~~~~

This module implements the CloudCIX API configurations module

This conf object lazyly loads the CLOUDCIX_SETTINGS_MODULE, and falls back
on the DJANGO_SETTINGS_MODULE for Django apps

Usage:

from cloudcix.conf import settings

base_url = settings.CLOUDCIX_API_URL
"""

import os
import importlib

from cloudcix.exceptions import ImproperlyConfigured

CLOUDCIX_ENVIRONMENT = 'CLOUDCIX_SETTINGS_MODULE'
DJANGO_ENVIRONMENT = 'DJANGO_SETTINGS_MODULE'


class LazySettings:
    """
    Lazy settings module. We want settings to be imported only when they
    are accessed, and not earlier
    """

    def __init__(self):
        self._wrapped = None

    def __getattr__(self, item):
        if self._wrapped is None:
            self._setup(item)
        return getattr(self._wrapped, item)

    def __setattr__(self, key, value):
        if key == '_wrapped':
            # Assign to __dict__ to avoid infinite __setattr__ loops
            self.__dict__[key] = value
        else:
            if self._wrapped is None:
                self._setup()
            setattr(self._wrapped, key, value)

    def __delattr__(self, key):
        if key == '_wrapped':
            raise TypeError('cannot delete _wrapped attribute')
        if self._wrapped is None:
            self._setup()
        delattr(self._wrapped, key)

    def _setup(self, *args):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has
        not previously configured the settings manually
        """
        module = os.environ.get(CLOUDCIX_ENVIRONMENT)
        if not module:
            module = os.environ.get(DJANGO_ENVIRONMENT)
        self._wrapped = Settings(module)


class Settings(object):

    def __init__(self, mod):
        mod = importlib.import_module(mod)
        for setting in dir(mod):
            if setting.isupper() and setting.startswith('CLOUDCIX_'):
                setattr(self, setting, getattr(mod, setting))

    def __setattr__(self, key, value):
        urls = (
            'CLOUDCIX_AUTH_URL',
            'CLOUDCIX_API_URL'
        )
        if key in urls and not value.endswith('/'):
            raise ImproperlyConfigured(
                '{} must end with a slash'.format(
                    key
                )
            )
        object.__setattr__(self, key, value)


settings = LazySettings()