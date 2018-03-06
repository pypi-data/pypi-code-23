import unittest
import os
import json
from mock import patch
from .api import get_or_create_pull_request
import logging
logger = logging.getLogger(__name__)

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


with open(os.path.join(__location__, 'json_samples/already_exists_created.json')) as f:
    data = f.read()
    already_exists_json = json.loads(data)

with open(os.path.join(__location__, 'json_samples/valid_created.json')) as f:
    data = f.read()
    created = json.loads(data)

with open(os.path.join(__location__, 'json_samples/valid_get.json')) as f:
    data = f.read()
    valid_get = json.loads(data)


def mocked_requests_post_created(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.content = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    return MockResponse(created, 201)


def mocked_requests_get_valid(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.content = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    return MockResponse(valid_get, 201)


def mocked_requests_get_invalid(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.content = json_data
            self.status_code = status_code

        def json(self):

            return self.json_data
    return MockResponse(valid_get, 400)


class TestGetOrCreateBranch(unittest.TestCase):

    @patch('requests.post', side_effect=mocked_requests_post_created)
    @patch('requests.get', side_effect=mocked_requests_get_invalid)
    def test_create(self, mock_get, mock_post):
        params = {
            "head": "test-branch",
            "base": "develop"
        }
        response_json = get_or_create_pull_request('foo.com', 'bwarren2', params)
        self.assertEqual(response_json['id'], 147363129)

    @patch('requests.get', side_effect=mocked_requests_get_valid)
    def test_get(self, mock_get):
        params = {
            "head": "test-branch",
            "base": "develop"
        }
        response_json = get_or_create_pull_request('foo.com', 'bwarren2', params)
        self.assertEqual(response_json['id'], 147611694)
