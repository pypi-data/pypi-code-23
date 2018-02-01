from .action_status import ActionStatus


class ActionTracker:
    """Action management class"""

    def __init__(self, action: str, workspace):
        """Initialize action tracker

        Parameters
        ----------
        action: str
            Action to track
        workspace: Workspace
            Workspace to track action in
        """
        self.action = action
        self.workspace = workspace

    def __enter__(self):
        self.workspace.state[self.action] = ActionStatus.started.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = (
            ActionStatus.finished
            if exc_tb is None
            else ActionStatus.failed
        )
        self.workspace.state[self.action] = status.value

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
        return self.workspace.state[self.action] is None

    def status(self):
        return self.workspace.state[self.action]
