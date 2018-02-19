import datetime
import os
from . import Project
from . import GitHistoryParser
from . import JiraApi


class SimpleTracker(object):
    def __init__(self, project):
        assert (isinstance(project, Project))
        self.parser = GitHistoryParser.GitHistoryParser(project)
        self.project = project
        self.events = []

    def load(self):
        if not os.path.isfile(self.project.get_log_path()):
            print('Please run python install.py ' + self.project.get_path())
            exit(1)

        with open(self.project.get_log_path()) as f:
            self.events = self.parser.parse_history(f.readlines())

    def track(self, date):
        events = self.get_to_track(date)
        to_track = datetime.timedelta(hours=self.project.get_hours_per_day()) / len(events)
        api = JiraApi()

        success = []
        for event in events:
            if api.track(self.project, event, to_track):
                success.append(event)

        return success

    def get_to_track(self, date):
        assert (isinstance(date, datetime.date))
        today_events = []
        for event in self.events:
            if event.get_event_date() == date and event.get_ticket():
                today_events.append(event)

        if not today_events:
            for event in self.events[::-1]:
                print(event.is_ticket_target())
                if event.get_event_date() < date and event.is_ticket_target():
                    today_events.append(event)
                if event.get_event_date() < date:
                    break

        return today_events
