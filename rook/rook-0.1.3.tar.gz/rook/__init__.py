"""This package implements real-time data collection capabilities on top of the python environment.

In order to use Rookout data collection service, the following components are needed:
- The Rook module package (this package).
- The Rookout Agent.
- The Rookout Web Service.

For further information, checkout rookout.com.

This package can be used in two ways:
- Importing using "from rook import auto_start" will start the Rook using the default configuration.
- Importing "from rook import Rook" allows to manually configure and start the Rook.
"""

# During development package structure is a bit different, so we extend the package dynamically
try:
    from . import lib
except ImportError:
    import os
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    __path__.append(root_dir)

# There appears to be issues if this code is loaded too late, so we load it early as possible
from .services.bdb_location_service import BdbLocationService as _BdbLocationService

from .interface import Rook
