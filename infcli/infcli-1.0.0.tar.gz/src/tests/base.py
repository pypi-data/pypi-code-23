# coding: utf-8
import json
from unittest import TestCase


class MockResponse(object):
    def __init__(self, status_code, content=None, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        if isinstance(self.content, dict):
            return self.content
        return json.loads(self.content)
