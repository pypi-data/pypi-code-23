import os

from python_agent.test_listener.entities.upload_reports_metadata import UploadReportsAgentData
from python_agent.test_listener.entities.upload_reports_request import UploadReportsRequest
from python_agent.test_listener.executors.anonymous_execution import AnonymousExecution


class UploadReports(AnonymousExecution):

    def __init__(self, config_data, labid, report_files, report_files_folder, source, report_type, has_more_requests):
        super(UploadReports, self).__init__(config_data, labid)
        self.report_files = report_files or []
        self.report_files_folder = report_files_folder or []
        self.source = source
        self.report_type = report_type
        self.has_more_requests = has_more_requests

    def execute(self):
        files = []
        for report_file in self.report_files:
            if os.path.isfile(report_file):
                files.append(open(report_file, "r"))
            else:
                print("The provided report file/folder '%s' doesn't exist" % report_file)

        for report_files_folder in self.report_files_folder:
            if os.path.isdir(report_files_folder):
                for report_file in os.listdir(report_files_folder):
                    files.append(open(report_file, "r"))
            else:
                print("The provided reports folder '%s' doesn't exist or is not a folder" % report_files_folder)

        for report_file in files[:-1]:
            self.upload_report(report_file, has_more_requests=True)

        # upload last report
        self.upload_report(files[-1], has_more_requests=self.has_more_requests)

    def upload_report(self, report_file, has_more_requests=False):
        upload_reports_agent_data = UploadReportsAgentData(self.config_data, self.labid, self.source, self.report_type,
                                                         self.has_more_requests)
        upload_reports_request = UploadReportsRequest(upload_reports_agent_data, report_file)
        self.backend_proxy.upload_reports(upload_reports_request)

