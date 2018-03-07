# coding: utf-8

from unittest.mock import Mock

from django.test import TestCase

from restify.task.client import AuthBase
from restify.task.client.auth import HeaderAuth


class AuthBaseTests(TestCase):
    def test_abstract_methods(self):
        self.assertRaises(NotImplementedError, lambda: AuthBase(None, None).inject_credentials(None))


class HeaderAuthTests(TestCase):
    def test_inject_credentials(self):
        username = 'username'
        token = 'token'

        auth = HeaderAuth(username, token)

        mock_request = Mock(headers={})
        auth.inject_credentials(mock_request)
        self.assertEqual(mock_request.headers, {
            'Authorization': 'apikey {0}:{1}'.format(username, token)
        })
