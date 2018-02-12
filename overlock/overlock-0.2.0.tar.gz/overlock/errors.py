"""Overlock-specific errors that can occur"""

class OverlockBaseException(Exception):
    def __init__(self, cause=None):
        if not cause:
            cause = "unknown"

        self.cause = cause

        super(OverlockBaseException, self).__init__()


class MessageSendError(OverlockBaseException):
    """Error sending message to daemon"""


class InvalidRelatedError(OverlockBaseException):
    """Tried to set 'related' to an unsupported value"""


class InvalidNodeIdError(OverlockBaseException):
    """Tried to spoof an invalid node id"""
