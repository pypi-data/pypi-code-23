import imp
import importlib
from unittest import TestCase

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from . import handlers as mock_handlers


class LoadHandlersTests(TestCase):
    def test_no_handler_in_settings(self):
        """Raise `ImproperlyConfigured` if no handlers module is setup in settings

        """
        with self.assertRaises(ImproperlyConfigured) as cm:
            handlers = importlib.import_module('djabberd.handlers')
            del settings.DJABBERD_API_HANDLERS

            imp.reload(handlers)

            self.assertIn("can not be empty", cm.exception.msg)

    def test_valid_handlers(self):
        handlers = importlib.import_module('djabberd.handlers')

        for handler_name in handlers.HANDLERS_NAMES:
            self.assertIs(getattr(handlers, handler_name),
                          getattr(mock_handlers, handler_name))
