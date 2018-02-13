__version__ = '0.1'
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
from .logger import critical, error, warning, info, debug
from .configuration import configure_as_library, configure