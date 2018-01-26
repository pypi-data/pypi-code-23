import enum


class ActionStatus(enum.Enum):
    """Action status list"""
    started = 'started'
    finished = 'finished'
    failed = 'failed'
    undefined = None
