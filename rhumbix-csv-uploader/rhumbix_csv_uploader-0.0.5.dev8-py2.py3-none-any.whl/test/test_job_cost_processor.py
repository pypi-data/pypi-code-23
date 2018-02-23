import unittest
import rhumbix_csv_uploader.job_cost_processor as processor
from rhumbix_csv_uploader.job_cost_processor import get_batch_status, post_data, read_job_cost_csv, transform_values
from rhumbix_csv_uploader.test.processor_test_config import delay_between_requests, company_key, api_key

job_cost_test_csv = "rhumbix_csv_uploader/test/exampleCSVs/rhumbix_job_cost_2.csv"
processor.company_key = company_key
processor.api_key = api_key

class TestTransformValues(unittest.TestCase):
    def test_transform_values(self):
        data = read_job_cost_csv(job_cost_test_csv)
        data = transform_values(data)
        assert(all([x in data[0].keys()
                    for x in ["job_number", "name", "cost_codes"]]))


class TestPostData(unittest.TestCase):
    def test_post_then_batch_status(self):
        data = read_job_cost_csv(job_cost_test_csv)
        data = transform_values(data)
        result = post_data(data)
        assert(result.status_code == 200), result.json()
        body = result.json()
        assert('batch_key' in body), result.json()
        batch_key = body["batch_key"]
        import time
        time.sleep(delay_between_requests)
        response = get_batch_status(batch_key)
        assert(response.status_code ==
               200), "response.status_code=%d" % response.status_code
        if(response.status_code == 200):
            body = response.json()
            assert(body["status"] in ["ACCEPTED",
                                      "PROCESSING", "COMPLETE"]), result.json()
            assert(len(body["errors"].items()) == 0)
