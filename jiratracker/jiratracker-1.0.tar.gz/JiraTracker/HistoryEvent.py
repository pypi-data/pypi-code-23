from . import HistoryLine
from . import Project


class HistoryEvent(object):
    def __init__(self, history_line1, history_line2, project):
        assert (isinstance(history_line1, HistoryLine.HistoryLine))
        assert (isinstance(history_line2, HistoryLine.HistoryLine))
        assert (isinstance(project, Project.Project))
        self.history_line1 = history_line1
        self.history_line2 = history_line2
        self.project = project

    def get_time_diff(self):
        return self.history_line2.get_time() - self.history_line1.get_time()

    def get_ticket(self):
        if isinstance(self.history_line1, HistoryLine.HistoryTicketLine):
            return self.history_line1.get_ticket()
        return None

    def get_event_date(self):
        return self.history_line2.get_time().date()

    def is_ticket_target(self):
        return isinstance(self.history_line2, HistoryLine.HistoryTicketLine)

    def __eq__(self, other):
        assert (isinstance(other, HistoryEvent))
        return self.history_line1.get_branch() == other.history_line1.get_branch() \
               and self.history_line1.get_time() == other.history_line1.get_time() \
               and self.history_line2.get_branch() == other.history_line2.get_branch() \
               and self.history_line2.get_time() == other.history_line2.get_time()
