import requests
import datetime
from . import Project
from . import HistoryEvent


class JiraApi(object):
    def track(self, project, event, time_to_track):
        assert (isinstance(project, Project.Project))
        assert (isinstance(event, HistoryEvent.HistoryEvent))
        assert (isinstance(time_to_track, datetime.timedelta))

        if not event.get_ticket():
            return

        data = {
            "timeSpentSeconds": time_to_track.seconds,
            "comment": "Tracked By JiraTracker"
        }

        response = requests.request(
            'POST', project.jira_url + '/rest/api/2/issue/' + event.get_ticket() + '/worklog',
            auth=(project.username, project.password),
            json=data
        )

        if response.status_code != 201:
            print(response)
            return

        return event
