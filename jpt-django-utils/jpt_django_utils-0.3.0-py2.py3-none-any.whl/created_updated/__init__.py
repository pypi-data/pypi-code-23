"""Created updated utils package.

Examples
--------
TODO

"""
import logging
from .models import *  # noqa
try:
    import rest_framework  # noqa
except ImportError:
    logging.info("DRF not found, skipping DRF imports")
else:
    from .serializers import *  # noqa
