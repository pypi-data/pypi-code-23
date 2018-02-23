import unittest
import rhumbix_csv_uploader.project_processor as processor
from rhumbix_csv_uploader.project_processor import get_batch_status, post_data, read_project_csv, transform_values
from rhumbix_csv_uploader.test.processor_test_config import delay_between_requests, company_key, api_key, api_url


project_test_csv = "rhumbix_csv_uploader/test/exampleCSVs/rhumbix_project.csv"
processor.company_key = company_key
processor.api_key = api_key
processor.api_url = api_url


class TestTransformValues(unittest.TestCase):
    def test_transform_values(self):
        data = read_project_csv(project_test_csv)
        data = transform_values(data)
        assert(isinstance(data[0]["is_active"], bool))


class TestPostData(unittest.TestCase):
    def test_post_then_batch_status(self):
        data = read_project_csv(project_test_csv)
        data = transform_values(data)
        result = post_data(data)
        assert(result.status_code == 200)
        body = result.json()
        assert('batch_key' in body)
        batch_key = body["batch_key"]
        import time
        time.sleep(delay_between_requests)
        response = get_batch_status(batch_key)
        assert(response.status_code == 200), "batch_key=%s, body=%s" % (
            batch_key, response.json())
        if(response.status_code == 200):
            body = response.json()
            assert(body["status"] in ["ACCEPTED", "PROCESSING", "COMPLETE"]), "body=%s" % body
            assert(len(body["errors"].items()) == 0)
