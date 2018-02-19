import sys
import Settings
import Tracker
import datetime


class JiraTracker(object):
    def main(self):
        try:
            settings = Settings.Settings(sys.argv[1])
            try:
                date = datetime.date.strftime(sys.argv[2], '%Y-%m-%d')
            except IndexError:
                date = datetime.datetime.now().date()
        except IndexError:
            print('Format: JiraTracker path_to_settings.yml date_to_track')
            sys.exit(1)

        for project in settings.get_projects():
            tracker = Tracker.SimpleTracker(project)
            tracker.load()
            tracked = tracker.track(date)
            for event in tracked:
                print("Successfully tracked", event.get_ticket())
            if not tracked:
                print("Nothing was tracked")


if __name__ == '__main__':
    jira_tacker = JiraTracker()
    jira_tacker.main()
