"""Version utils package.

Adds the ability to track a model's 'version' when it's edited and saved.

Examples
--------
TODO

"""
import logging

from .models import *  # noqa
from .fields import *  # noqa
try:
    import rest_framework  # noqa
except ImportError:
    logging.info("DRF not found, skipping DRF imports")
else:
    from .serializers import *  # noqa
