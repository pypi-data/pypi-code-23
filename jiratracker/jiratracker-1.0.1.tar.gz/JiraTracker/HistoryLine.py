import datetime


class HistoryLine(object):
    def __init__(self, time, branch):
        assert (isinstance(time, datetime.datetime))
        assert (isinstance(branch, str))
        self.time = time
        self.branch = branch

    def get_time(self):
        return self.time

    def get_branch(self):
        return self.branch


class HistoryNonTicketLine(HistoryLine):
    pass


class HistoryTicketLine(HistoryLine):
    def __init__(self, time, branch, ticket):
        super().__init__(time, branch)
        assert (isinstance(ticket, str))
        self.ticket = ticket

    def get_ticket(self):
        return self.ticket
