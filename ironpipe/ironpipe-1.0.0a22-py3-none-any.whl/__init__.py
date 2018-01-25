# Ironpipe Python bindings
# API docs at http://ironpipe.io/docs

# Configuration variables

api_key = None
api_base = 'https://api.ironpipe.io/'
api_version = None

# Set to either 'debug' or 'info', controls console logging
log = None

# API
from ironpipe.api import *

# Errors
from ironpipe.error import (  # noqa
    IronpipeError
)
