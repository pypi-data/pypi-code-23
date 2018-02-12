import logging
import os

from .state import WorkspaceState
from .bind import Bind
from .action_status import ActionStatus


def _get_logger():
    return logging.getLogger(__name__)


class ActionTracker:
    """Manages and monitors actions"""

    def __init__(self, action: str, state_path: str, path=None):
        """Creates a new action tracker

        Attributes
        ----------
        action: str
            Name of the action to track
        state_path: str
            Path of the state file to store information about the action state
        path: str, optional
            Path of the file to check for existatnce on exit
            
            This path is checked only if the tracker 
            is used as a context manager
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
        """WorkspaceState object linked to `self.state_path`"""
        return WorkspaceState(self.state_path)

    def __enter__(self):
        """Context manager enter"""
        self.state[self.action] = ActionStatus.started.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
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
        """Returns True if the action has started and is pending"""
        return self._status_flag(ActionStatus.started)

    def finished(self):
        """Returns True if the action has finished"""
        return self._status_flag(ActionStatus.finished)

    def failed(self):
        """Returns True if the action has failed"""
        return self._status_flag(ActionStatus.failed)

    def undefined(self):
        """Returns True if the action state is not defined"""
        return self.state[self.action] is None

    def status(self):
        """Returns a string representation of the current action status"""
        return self.state[self.action]
