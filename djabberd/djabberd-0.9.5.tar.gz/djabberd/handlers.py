# Load handlers defined in `settings.DJABBERD_API_HANDLERS`

import importlib
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


HANDLERS_KEY = 'DJABBERD_API_HANDLERS'
HANDLERS_NAMES = (
    'user_authentication',
    'user_exists',
    'retrieve_user_roster',
    'archive_store',
    'archive_get',
)


def _load_handlers():
    handlers_module_name = getattr(settings, HANDLERS_KEY, None)
    if handlers_module_name is None:
        raise ImproperlyConfigured(
            "The {} setting can not be empty.".format(HANDLERS_KEY))

    handlers_module = importlib.import_module(handlers_module_name)

    module = sys.modules[__name__]
    for handler in HANDLERS_NAMES:
        new_handler = getattr(handlers_module, handler)
        setattr(module, handler, new_handler)


_load_handlers()
