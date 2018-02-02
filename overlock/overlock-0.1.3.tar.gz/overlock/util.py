import logging
import sys
import traceback
import datetime
import time
import contextlib
from functools import partial
from abc import abstractmethod

from . import errors
from .state import client_state


class partialmethod(partial):
    """Like Python 3's partialmethod but backported for Python 2
    """
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return partial(self.func, instance, *(self.args or ()), **(self.keywords or {}))


class LogMixin(object):

    def __init__(self):
        self._related = []

    @abstractmethod
    def post_log(self, log_data, related=[], node_id=None):
        """Post a log message to the agent

        Args:
            log_data (dict): log data to post
            related (list, optional): List of node ids that this message is also
                related to
            node_id (str, optional): Node id to log as - can be passed to
                impersonate another device to log for them (for example if its
                an embedded device and doesn't have the capability to run this
                client itself)
        """

    @contextlib.contextmanager
    def log_as(self, node_id):
        """Make it so log messages will be logged as another node

        After exiting the context manager, node id will be reset. This allows
        for nesting of context managers, but node id hsould not be changed mid-
        context manager or weird behaviour will result

        Args:
            node_id (str): ID of node to log as

        Example:

            .. code-block:: python

                with logger.log_as("abc123"):
                    # will be logged with node_id=123 to daemon
                    logger.info("Message was %s", message)
        """

        logging_as_before = client_state._node_id

        client_state._node_id = node_id

        yield

        client_state._node_id = logging_as_before

    def _sanitise_related(self, related):
        """Convert 'related' into a list and make sure the format/types are
        correct
        """
        if not isinstance(related, (list, tuple)):
            related = [related]

        if not all(isinstance(i, str) for i in related):
            raise errors.InvalidRelatedError

        return related

    @contextlib.contextmanager
    def with_related(self, related):
        """Add 'related' nodes to log messages

        This will be sent in the 'meta' field to the daemon along with any other
        metadata

        Args:
            related (str, list, tuple): either a single related node or a list
                of related nodes to log along with the message

        Example:

            .. code-block:: python

                with logger.with_related(["abc123", "def456"]):
                    # Additional related nodes will be sent to daemon
                    logger.info("auiuhtr")

        Todo:

            Make this take *related instead so they can just be passed like
            with_related(a, b, c)?
        """

        related = self._sanitise_related(related)

        self._related = related

        yield

        self._related = []

    def log(self, severity, message, *args, **kwargs):
        """ Construct a log message to post """

        # XXX utc?
        now = datetime.datetime.now()

        log_data = {
            "message": (message % args),
            "severity": severity,
            "ts": int(time.mktime(now.timetuple())+now.microsecond/1000000.0),
            "related": self._related,
        }

        try:
            kwargs.pop("exc_info")
        except KeyError:
            pass
        else:
            if not sys.exc_info()[2]:
                log_data["traceback"] = "No traceback"
            else:
                log_data["traceback"] = traceback.format_exc()

        try:
            related = kwargs.pop("related")
        except KeyError:
            pass
        else:
            log_data["related"] = self._sanitise_related(related)

        self.post_log(log_data, **kwargs)

    debug = partialmethod(log, logging.DEBUG)
    info = partialmethod(log, logging.INFO)
    warning = partialmethod(log, logging.WARNING)
    error = partialmethod(log, logging.ERROR)
    critical = partialmethod(log, logging.CRITICAL)
