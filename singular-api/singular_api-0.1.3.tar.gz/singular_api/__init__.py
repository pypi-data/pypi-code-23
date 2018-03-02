from .models import (
        Activity, Comment, Context,
        ContextTime, TeamMember, Team,
        User, BaseModel
        )
from .client import Client

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import (
            NullHandler, getLogger
            )
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

getLogger(__name__).addHandler(NullHandler())
