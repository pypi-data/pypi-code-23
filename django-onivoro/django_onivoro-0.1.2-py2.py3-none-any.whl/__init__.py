# coding: utf-8
import logging
from custom_settings.loader import load_settings


load_settings(__name__)

# configuring no-op handler for our logger. users should add specific handlers for this.
log = logging.getLogger("django-onivoro")
log.addHandler(logging.NullHandler())

__version__ = '0.1.1'
