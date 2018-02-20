import datetime

from beautifultable import BeautifulTable

from sokot.configuration import SokotConfiguration
from sokot.requester import SokotRequester

DAILY_WORKING_API = '/daily-workings?start={}&end={}&additionalFields=currentDateEmployee'


class SokotAggretator():
    def __init__(self):
        self._config = SokotConfiguration()
        self._sprints = self._culc_sprint()
        self._requester = SokotRequester()

    def _culc_sprint(self):
        sprints = []
        start_day = self._config.get_scrum_start_day()
        sprint_start = start_day
        while True:
            if sprint_start > datetime.date.today():
                break
            sprint_end = sprint_start + datetime.timedelta(days=13)
            sprint = (sprint_start, sprint_end)
            sprints.append(sprint)
            sprint_start = sprint_end + datetime.timedelta(days=1)
        return sprints

    def _print_warning(self, record):
        last_name = record['currentDateEmployee']['lastName']
        first_name = record['currentDateEmployee']['firstName']
        error_date = record['date']
        print('{} {}さんの{}の入力にエラーがあります'.format(last_name, first_name, error_date))

    def _aggregate_sprint(self, members, sprint_start, sprint_end):
        token = self._config.get_token()
        resp = self._requester.get(DAILY_WORKING_API.format(sprint_start, sprint_end), token)
        sum_min = 0
        for daily_record in resp:
            for record in daily_record['dailyWorkings']:
                if record['currentDateEmployee']['code'] in members:
                    if record['isError']:
                        self._print_warning(record)
                    else:
                        sum_min += record['overtime']
        return round(sum_min / 60, 2)

    def aggregate(self, agg_type):
        table = BeautifulTable()
        group_names = list(self._config.list_group().keys())
        table.column_headers = ["Sprint No."] + group_names

        sprint_no = 0
        for sprint in self._sprints:
            sprint_no += 1
            sprint_start, sprint_end = sprint[0], sprint[1]
            sprint_str = "Sprint #{} ({} - {})".format(sprint_no, sprint_start, sprint_end)
            group_result = []
            for _, members in self._config.list_group().items():
                result = self._aggregate_sprint(members, sprint_start, sprint_end)
                group_result.append(result)
            table.append_row([sprint_str] + group_result)
        return table
