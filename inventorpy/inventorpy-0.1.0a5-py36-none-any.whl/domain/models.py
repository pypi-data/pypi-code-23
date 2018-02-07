import bcrypt
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
    def __init__(self, uuid, first_name: str, last_name: str, email: str,
                 password: str=None) -> None:
        self.uuid = uuid
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = None
        if password:
            self.password_hash = self.hash_password(password)

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf8'),
            self.password_hash.encode('utf8')
        )

    def hash_password(self, password):
        return bcrypt.hashpw(
            password.encode('utf8'),
            bcrypt.gensalt(10)
        ).decode()


class Issue:
    def __init__(self, uuid: UUID,
                 reporter: User, description: str) -> None:
        self.uuid = uuid
        self.reporter = reporter
        self.description = description
        self.state = IssueState.AwaitingTriage
        self.events = []
        self._assignments = []
        self.priority = None
        self.category = None

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
                IssueAssignedToEngineer(self.uuid, assigned_to, assigned_by)
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
