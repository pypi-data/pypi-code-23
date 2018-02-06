"""
Command objects are small objects that represent a STATE-CHANGING action
that can happen in the system. They represent instructions from an external
agent ex; user, cron job, or other services.

Should have a name in an imperative tense; ReportIssue, PrepareUpload,
RemoveItemFromCart, ScheduleNewServiceCall, BeginPaymentProcess.

The list of all commands available should be a list of all supported
operations in the domain model.
"""
from typing import NamedTuple
from uuid import UUID

from inventorpy.domain.models import IssuePriority


def command(cls):
    setattr(cls, 'is_cmd', True)
    setattr(cls, 'is_event', False)
    setattr(cls, 'cmd_id', None)
    return cls


@command
class ReportIssueCommand(NamedTuple):
    issue_id: UUID
    reporter_name: str
    reporter_email: str
    problem_description: str


@command
class TriageIssueCommand(NamedTuple):
    issue_id: UUID
    category: str
    priority: IssuePriority


@command
class AssignIssueCommand(NamedTuple):
    issue_id: UUID
    assigned_to: str
    assigned_by: str


@command
class PickIssueCommand(NamedTuple):
    issue_id: UUID
    picked_by: str


@command
class ScheduleNewJobCommand(NamedTuple):
    job_id: UUID
    location_id: UUID
    scheduled_by: UUID
