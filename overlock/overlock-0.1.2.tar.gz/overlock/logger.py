import functools
import logging

from . import errors
from .util import LogMixin
from .client import OverlockRequestsClient
from .state import client_state

logger = logging.getLogger(__name__)


class OverlockLogger(LogMixin):
    def __init__(self, client_type=OverlockRequestsClient):
        super(OverlockLogger, self).__init__()

        cmds = [
            "update_state",
            "update_metadata",
            "lifecycle_event",
            "post_log",
        ]

        self._client = client_type()

        for c in cmds:
            wrapped = OverlockLogger.wrap_client(getattr(self._client, c))
            setattr(self, c, wrapped)

    @staticmethod
    def wrap_client(meth):

        @functools.wraps(meth)
        def call_meth(*args, **kwargs):
            if "node_id" not in kwargs:
                kwargs.update(node_id=client_state._node_id)

            if kwargs.get("node_id"):
                if not isinstance(kwargs["node_id"], str):
                    raise errors.InvalidNodeIdError

            try:
                meth(*args, **kwargs)
            except errors.OverlockBaseException:
                logger.exception("Error calling %s", meth)
            except Exception:
                logger.exception("Unexpected error calling %s", meth)

        return call_meth
