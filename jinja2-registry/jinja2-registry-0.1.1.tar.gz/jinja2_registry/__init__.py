"""jinja2-registry: Easy handling of multiple loaders and default contexts"""

from __future__ import absolute_import

__version__ = '0.1.1'
__author__ = '3point Science'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016 3point Science'

from .base import (
    Renderer,
    Registry,
    register_loader,
    register_filesystem_loader,
    set_environment_options,
    set_global_defaults,
    set_environment_filters,
)
