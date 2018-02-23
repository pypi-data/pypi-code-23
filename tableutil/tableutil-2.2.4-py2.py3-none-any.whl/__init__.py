# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
from .cell import (Cell,
                   make_uri_cell)
from .table import Table
from .table_html import TABLE_CSS
from .row import Row
from .constants import (TableSeparators,
                        Justify,
                        CLASSES,
                        HEADING,
                        JUSTIFY,
                        MAX,
                        KEY,
                        VALUE,
                        CONVERT,
                        PROPERTY,
                        DUMMY,
                        DUMMY_HEADINGS,
                        KEY_VALUE_HEADINGS)

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
