# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import json
from . import core
import datetime
import requests

class MockResponse(object):
    def __init__(self, body, status_code):
        self.body = body
        self.status_code = status_code

    def text(self):
        return self.body

    def json(self):
        return json.loads(self.body)

class SchedyDBTest(unittest.TestCase):
    def setUp(self):
        config = StringIO('{"root": "schedy://schedy.io/", "email": "test@schedy.io", "token": "token"}')
        self.db = core.SchedyDB(config)

    def test_config(self):
        self.assertEqual(self.db.root, 'schedy://schedy.io/')
        self.assertEqual(self.db.email, 'test@schedy.io')
        self.assertEqual(self.db.api_token, 'token')

    @patch('requests.Session')
    def test_authenticate(self, sess_mock):
        # Test can authenticate
        exp_date = datetime.datetime.now() + datetime.timedelta(days=1)
        resp_mock = sess_mock.return_value.request.return_value
        resp_mock.status_code = 200
        resp_mock.json.return_value = {'token': 'jwt.token.valid', 'expiresAt': exp_date.timestamp()}
        self.db._authenticate()
        self.assertEqual(self.db._jwt_token.token_string, 'jwt.token.valid')
        self.assertEqual(self.db._jwt_token.expires_at, exp_date)
        # Test does not request token second time
        resp_mock.json.return_value = {}
        resp = self.db._authenticated_request('GET', '/')
        # Test session not recreated
        sess_mock.assert_called_once()
        # Test not reauthenticated
        sess_mock.return_value.request.assert_('GET')

