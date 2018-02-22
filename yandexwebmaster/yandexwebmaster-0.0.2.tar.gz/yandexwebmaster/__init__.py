# coding: utf-8

__version__ = '0.0.2'
__author__ = 'Danillab'

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from .core import ApiError, YandexWebmaster

