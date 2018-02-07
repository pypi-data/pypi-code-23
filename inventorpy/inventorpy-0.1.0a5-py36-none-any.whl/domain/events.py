from typing import NamedTuple
from uuid import UUID


def event(cls):
    setattr(cls, 'is_cmd', False)
    setattr(cls, 'is_event', True)
    setattr(cls, 'event_id', None)
    return cls


@event
class IssueAssignedToEngineer(NamedTuple):
    issue_id: UUID
    assigned_to: str
    assigned_by: str


@event
class IssueReassigned(NamedTuple):
    issue_id: UUID
    previous_assignee: str
