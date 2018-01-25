import time
import itertools

from adobe_analytics.report import Report
from adobe_analytics.report_definition import ReportDefinition


class ReportDownloader:
    def __init__(self, suite):
        self.suite = suite

    def download(self, obj):
        report = self._to_report(obj)
        report.raw_response = self.check_until_ready(report)
        report.parse()
        return report

    def _to_report(self, obj):
        assert isinstance(obj, (Report, ReportDefinition, int, float))

        if isinstance(obj, Report):
            return obj
        elif isinstance(obj, ReportDefinition):
            return self.queue(obj)
        else:
            return Report(report_id=obj)

    def queue(self, report_definition):
        json_definition = report_definition.inject_suite_id(self.suite.id)
        request_data = self._build_request_data_definition(json_definition)

        client = self.suite.client
        response = client.request(
            api="Report",
            method="Queue",
            data=request_data
        )
        report = Report(report_id=response["reportID"])
        print("ReportID:", report.id)
        return report

    def check_until_ready(self, report, max_attempts=-1):
        """ max_attemps is only designed for easier testing """
        counter = itertools.count() if max_attempts == -1 else range(max_attempts)

        for poll_attempt in counter:
            response = self.check(report)
            if response is not None:
                return response

            interval = self._sleep_interval(poll_attempt)
            time.sleep(interval)

    @staticmethod
    def _sleep_interval(poll_attempt):
        exponential = 5 * 2**poll_attempt
        return min(exponential, 300)  # max 5 min sleep

    def check(self, obj):
        report = self._to_report(obj)
        request_data = self._build_request_data_id(report)

        client = self.suite.client
        response = client.request(
            api="Report",
            method="Get",
            data=request_data
        )
        is_ready = ("error" not in response) or (response["error"] != "report_not_ready")
        if is_ready:
            return response
        return None

    def cancel(self, report):
        request_data = self._build_request_data_id(report)

        client = self.suite.client
        response = client.request(
            api='Report',
            method='Cancel',
            data=request_data
        )
        return response

    @staticmethod
    def _build_request_data_definition(json_definition):
        assert json_definition["reportSuiteID"] is not None
        return {"reportDescription": json_definition}

    @staticmethod
    def _build_request_data_id(report):
        return {"reportID": report.id}
