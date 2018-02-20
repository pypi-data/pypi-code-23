import more_itertools
import pandas as pd
from retrying import retry
import logging

from adobe_analytics.classifications.classification_job import ClassificationJob

logger = logging.getLogger(__name__)

BASE_WAIT_CLASSIFICATION = 2.5 * 10**3  # 2.5s -> 5s on first retry
MAX_WAIT_CLASSIFICATION = 20 * 10**3  # 20s


class ClassificationUploader:
    def __init__(self, client, suite_ids, variable_id, data, email, description="",
                 check_suite_compatibility=True, export_results=False, overwrite_conflicts=True):
        self._validate_data(data)

        self._client = client
        self.suite_ids = suite_ids
        self.variable_id = variable_id
        self.header, self.values = self._header_and_values(data)

        self.email = email
        self.description = description
        self.export_results = export_results
        self.check_suite_compatibility = check_suite_compatibility
        self.overwrite_conflicts = overwrite_conflicts

    @staticmethod
    def _validate_data(data):
        assert isinstance(data, pd.DataFrame), "Please pass data in form of a pandas DataFrame."
        assert data.columns[0] == "Key", "First column must correspond to the variable and be called 'Key'."
        assert data.isnull().sum().sum() == 0, "DataFrame must not contain missing values."

    @staticmethod
    def _header_and_values(data):
        header = list(data.columns)
        values = data.values.tolist()
        return header, values

    def upload(self):
        chunks = more_itertools.chunked(iterable=self.values, n=ClassificationJob.PAGE_SIZE)
        for chunk in chunks:
            self._upload_job(values=chunk)

    def _upload_job(self, values):
        job = self._create_import()

        job.add_data(values)
        job.commit()
        self.check_status_until_finished(job)

    def _create_import(self):
        response = self._client.request(
            api="Classifications",
            method="CreateImport",
            data={
                "rsid_list": self.suite_ids,
                "element": self.variable_id,
                "header": self.header,
                "description": self.description,
                "email_address": self.email,
                "check_divisions": self.check_suite_compatibility,
                "export_results": self.export_results,
                "overwrite_conflicts": self.overwrite_conflicts
            }
        )
        job_id = response["job_id"]
        logger.info("Job ID: {}".format(job_id))
        return ClassificationJob(client=self._client, job_id=job_id)

    @staticmethod
    @retry(retry_on_result=lambda x: "completed" not in x,
           wait_exponential_multiplier=BASE_WAIT_CLASSIFICATION, wait_exponential_max=MAX_WAIT_CLASSIFICATION)
    def check_status_until_finished(job):
        return job.check_status()
