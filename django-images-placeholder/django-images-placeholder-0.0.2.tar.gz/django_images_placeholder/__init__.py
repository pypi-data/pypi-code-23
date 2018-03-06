# coding: utf-8

from __future__ import absolute_import, unicode_literals

import django

__all__ = ['VERSION']


try:
    import pkg_resources
    VERSION = pkg_resources.get_distribution('django-images-placeholder').version
except Exception:
    VERSION = 'unknown'


# Code that discovers files or modules in INSTALLED_APPS imports this module.

urls = ('django_images_placeholder',)

default_app_config = 'django_images_placeholder.apps.DjangoImagesPlaceholderConfig'
