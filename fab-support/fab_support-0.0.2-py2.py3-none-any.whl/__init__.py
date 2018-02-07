# -*- coding: utf-8 -*-

"""Top-level package for fab_support."""

__author__ = """Humphrey Drummond"""
__email__ = 'hum3@drummond.info'
__version__ = '0.0.2'


from .env_support import *
from .stages_support import *
from .pelican import *
from .utils import *

set_stages = stages_support.set_stages
deploy = pelican.deploy

__all__ = ['set_stages', 'deploy',]
