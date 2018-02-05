import logging
import os

from .state import WorkspaceState
from .bind import Bind
from .action_status import ActionStatus


def _get_logger():
    return logging.getLogger(__name__)


class ActionTracker:
    """Action management class"""

    def __init__(self, action: str, state_path: str, path=None):
        """Initialize action tracker

        Parameters
        ----------
        action: str
            Action to track
        state_path: str
            State to track the action in
        path: str
            Check the path for existence on exit
        """
        assert isinstance(action, str)
        assert isinstance(state_path, str)

        self.action = action
        self.state_path = state_path
        self.path = path

    def __repr__(self):
        return '<ActionTracker({})>'.format(self.action)

    @property
    def state(self) -> WorkspaceState:
        return WorkspaceState(self.state_path)

    def __enter__(self):
        self.state[self.action] = ActionStatus.started.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        there_is_no_exception = exc_tb is None
        file_exists = self.path is None or os.path.exists(self.path)

        status = (
            ActionStatus.finished
            if there_is_no_exception and file_exists
            else ActionStatus.failed
        )

        if status is ActionStatus.failed:
            if not there_is_no_exception:
                _get_logger().info('Fail cause: {}'.format(exc_tb))
            elif not file_exists:
                _get_logger().info("File doesn't exist: {}".format(self.path))

        self.state[self.action] = status.value

    def _status_flag(self, status):
        return self.status() == status.value

    def started(self):
        """Returns True if action has started and is pending"""
        return self._status_flag(ActionStatus.started)

    def finished(self):
        """Returns True if action has finished"""
        return self._status_flag(ActionStatus.finished)

    def failed(self):
        """Returns True if action has failed"""
        return self._status_flag(ActionStatus.failed)

    def undefined(self):
        return self.state[self.action] is None

    def status(self):
        return self.state[self.action]
