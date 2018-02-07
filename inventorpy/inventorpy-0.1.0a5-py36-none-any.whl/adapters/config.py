from inventorpy.adapters import views
from inventorpy.domain import commands, events
from inventorpy.domain.ports import MessageBus
from inventorpy.services import event_handlers, command_handlers
from .emails import LoggingEmailSender
from .orm import SqlAlchemy


class Inventorpy:
    def __init__(self,
                 database=SqlAlchemy,
                 database_uri='sqlite://',
                 message_bus=MessageBus,):
        self._db = database(database_uri)
        self._db.create_schema()
        self._bus = message_bus()
        self._db.set_message_bus(self._bus)
        self._init_subscriptions()

    def _init_subscriptions(self):
        self._bus.subscribe_to(
            commands.ReportIssueCommand,
            command_handlers.ReportIssueHandler(self._db.unit_of_work_manager)
        )
        self._bus.subscribe_to(
            commands.TriageIssueCommand,
            command_handlers.TriageIssueHandler(self._db.unit_of_work_manager)
        )
        self._bus.subscribe_to(
            commands.AssignIssueCommand,
            command_handlers.AssignIssueHandler(self._db.unit_of_work_manager)
        )
        self._bus.subscribe_to(
            events.IssueAssignedToEngineer,
            event_handlers.IssueAssignedHandler(
                views.IssueViewBuilder(self._db),
                LoggingEmailSender()
            )
        )

    def get_issue_list(self):
        return views.IssueListBuilder(self._db).fetch()

    def report_issue(self, issue_id, **kwargs):
        cmd = commands.ReportIssueCommand(issue_id, **kwargs)
        self._bus.handle(cmd)
