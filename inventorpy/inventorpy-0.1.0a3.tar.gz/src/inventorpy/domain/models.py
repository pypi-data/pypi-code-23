from uuid import UUID
from enum import Enum
from .events import IssueAssignedToEngineer


class IssueState(Enum):
    AwaitingTriage = 0
    AwaitingAssignment = 1
    ReadyForWork = 2


class IssuePriority(Enum):
    NotPrioritised = 0
    Low = 1
    Normal = 2
    High = 3
    Urgent = 4


class User:
    def __init__(self, first_name: str, email: str) -> None:
        self.first_name = first_name
        self.email = email


class Issue:
    def __init__(self, issue_id: UUID,
                 reporter: User, description: str) -> None:
        self.id = issue_id
        self.reporter = reporter
        self.description = description
        self.state = IssueState.AwaitingTriage
        self.events = []
        self._assignments = []

    @property
    def current_assignment(self):
        """Return the latest assignment, or None if not assigned"""
        if not self._assignments:
            return None
        return self._assignments[-1]

    def triage(self, priority: IssuePriority, category: str) -> None:
        self.priority = priority
        self.category = category
        self.state = IssueState.AwaitingAssignment

    def assign(self, assigned_to, assigned_by=None):
        self._assignments.append(Assignment(assigned_to, assigned_by))
        self.state = IssueState.ReadyForWork

        if assigned_to != assigned_by:
            self.events.append(
                IssueAssignedToEngineer(self.id, assigned_to, assigned_by)
            )


class Assignment:
    def __init__(self, assigned_to, assigned_by):
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by

    def is_reassignment_from(self, other):
        if other is None:
            return False
        if other.assigned_to == self.assigned_to:
            return False
        return True
