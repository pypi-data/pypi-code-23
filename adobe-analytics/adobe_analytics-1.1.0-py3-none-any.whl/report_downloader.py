import time
import itertools
import pandas as pd

from adobe_analytics.report_definition import ReportDefinition
from adobe_analytics.parse import parse


class ReportDownloader:
    def __init__(self, suite):
        self.suite = suite

    def download(self, obj):
        report_id = self._to_report_id(obj)
        first_response = self.check_until_ready(report_id)
        raw_responses = [first_response]

        if "totalPages" in first_response["report"]:
            other_responses = self._download_other_pages(report_id, first_response)
            raw_responses += other_responses
        return self._to_stacked_dataframe(raw_responses)

    def _to_report_id(self, obj):
        assert isinstance(obj, (ReportDefinition, int, float))

        if isinstance(obj, ReportDefinition):
            return self.queue(obj)
        else:
            return int(obj)

    def queue(self, report_definition):
        raw_definition = report_definition.inject_suite_id(self.suite.id)
        request_data = self._build_request_data_definition(raw_definition)

        client = self.suite.client
        response = client.request(
            api="Report",
            method="Queue",
            data=request_data
        )
        report_id = int(response["reportID"])
        print("ReportID:", report_id)
        return report_id

    @staticmethod
    def _build_request_data_definition(json_definition):
        assert json_definition["reportSuiteID"] is not None
        return {"reportDescription": json_definition}

    def check_until_ready(self, report_id, max_attempts=-1):
        counter = itertools.count() if max_attempts == -1 else range(max_attempts)

        for poll_attempt in counter:
            response = self.get_attempt(report_id)
            if response is not None:
                return response

            interval = self._sleep_interval(poll_attempt)
            time.sleep(interval)

    def get_attempt(self, report_id, page_number=1):
        client = self.suite.client
        try:
            response = client.request(
                api="Report",
                method="Get",
                data={
                    "reportID": report_id,
                    "page": page_number
                }
            )
            return response
        except FileNotFoundError:
            return None

    @staticmethod
    def _sleep_interval(poll_attempt):
        exponential = 5 * 2**poll_attempt
        return min(exponential, 300)  # max 5 min sleep

    def _download_other_pages(self, report, raw_response):
        """ data warehouse requests are returned in paged format """
        total_page_count = raw_response["report"]["totalPages"]
        print("total page count:", total_page_count)

        raw_responses = list()
        for page_number in range(2, total_page_count+1):
            print("page number:", page_number)
            raw_response = self.get_attempt(report_id=report, page_number=page_number)
            raw_responses.append(raw_response)
        return raw_responses

    @staticmethod
    def _to_stacked_dataframe(raw_responses):
        dfs = [parse(raw_response) for raw_response in raw_responses]
        return pd.concat(dfs, ignore_index=True)

    def cancel(self, report_id):
        """ Cancels a requested report. When report is ready it can't be canceled anymore """
        client = self.suite.client
        response = client.request(
            api='Report',
            method='Cancel',
            data={
                "reportID": int(report_id)
            }
        )
        return response
