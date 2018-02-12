import enum


class ActionStatus(enum.Enum):
    """List of action statuses"""
    started = 'started'
    finished = 'finished'
    failed = 'failed'
    undefined = None
