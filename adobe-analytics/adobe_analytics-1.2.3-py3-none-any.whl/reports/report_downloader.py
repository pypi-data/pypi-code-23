import pandas as pd
from retrying import retry
import logging

from adobe_analytics.reports.report_definition import ReportDefinition
from adobe_analytics.reports.parse import parse

logger = logging.getLogger(__name__)

BASE_WAIT_REPORT = 2.5 * 10**3  # 2.5s -> 5s on first retry
MAX_WAIT_REPORT = 5 * 60 * 10**3  # 5min


class ReportDownloader:
    def __init__(self, suite):
        self.suite = suite

    def download(self, obj):
        report_id = self._to_report_id(obj)
        first_response = self.get_report(report_id)
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
        logger.info("ReportID: {}".format(report_id))
        return report_id

    @staticmethod
    def _build_request_data_definition(json_definition):
        assert json_definition["reportSuiteID"] is not None
        return {"reportDescription": json_definition}

    @retry(retry_on_exception=lambda x: isinstance(x, FileNotFoundError),
           wait_exponential_multiplier=BASE_WAIT_REPORT, wait_exponential_max=MAX_WAIT_REPORT)
    def get_report(self, report_id, page_number=1):
        client = self.suite.client
        response = client.request(
            api="Report",
            method="Get",
            data={
                "reportID": report_id,
                "page": page_number
            }
        )
        return response

    def _download_other_pages(self, report, raw_response):
        """ data warehouse requests are returned in paged format """
        total_page_count = raw_response["report"]["totalPages"]
        print("total page count:", total_page_count)

        raw_responses = list()
        for page_number in range(2, total_page_count+1):
            print("page number:", page_number)
            raw_response = self.get_report(report_id=report, page_number=page_number)
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
                "reportID": report_id
            }
        )
        return response
