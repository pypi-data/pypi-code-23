"""
Command handlers are stateless objects that orchestrate the behaviour of
a system.

"Glue code"

Every Command is handled by exactly one command handler.

Should all have the same structure:
    1. Fetch the current state from our persistent storage.
    2. Update the current state.
    3. Persist the new state.
    4. Notify andy external systems that our state has changed.

Usually avoid if statements, loops, and other logic code.
"""
from inventorpy.domain.models import User, Issue
from inventorpy.domain.ports import UnitOfWorkManager


class ReportIssueHandler:
    """Command handlers are initialized with the a UnitOfWorkManager
    Responsible for starting a Unit Of Work and committing the work
    when finished (keeping rule #1: clearly define the beginning and end
                   of use cases)

    The handle method depends on an abstraction and doesn't care what kind
    of session is being used (rule #2)

    Simple 'glue code', being moved to the outer edges of our system (rule #3)
    """

    def __init__(self, uow_manager: UnitOfWorkManager):
        self.uow_manager = uow_manager

    def __call__(self, cmd):
        self.handle(cmd)

    def handle(self, cmd):

        with self.uow_manager.start() as tx:
            user = tx.users.get(cmd.reporter_uuid)
            issue = Issue(cmd.issue_uuid, user, cmd.problem_description)
            tx.issues.add(issue)
            tx.commit()


class TriageIssueHandler:
    def __init__(self, uow_manager: UnitOfWorkManager):
        self.uow_manager = uow_manager

    def handle(self, cmd):
        with self.uow_manager.start() as tx:
            issue = tx.issues.get(cmd.issue_id)
            issue.triage(cmd.priority, cmd.category)
            tx.commit()


class PickIssueHandler:
    def __init__(self, uow_manager: UnitOfWorkManager):
        self.uow_manager = uow_manager

    def handle(self, cmd):
        with self.uow_manager.start() as tx:
            issue = tx.issues.get(cmd.issue_id)
            issue.assign(cmd.picked_by)
            tx.commit()


class AssignIssueHandler:
    def __init__(self, uow_manager: UnitOfWorkManager):
        self.uow_manager = uow_manager

    def handle(self, cmd):
        with self.uow_manager.start() as tx:
            issue = tx.issues.get(cmd.issue_id)
            issue.assign(cmd.assigned_to, cmd.assigned_by)
            tx.commit()
