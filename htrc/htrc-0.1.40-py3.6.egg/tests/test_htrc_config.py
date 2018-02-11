from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import sys
if sys.version_info.major == 2:
    from mock import Mock, patch, PropertyMock
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch, PropertyMock

from io import BytesIO  # used to stream http response into zipfile.
import os.path # used to test the defaults for testing
from tempfile import NamedTemporaryFile, mkdtemp
import unittest2 as unittest

import htrc.config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_vols = ['mdp.39015050817181', 'mdp.39015055436151',
            'mdp.39015056169157', 'mdp.39015050161697', 'mdp.39015042791874']

        self.config_path = NamedTemporaryFile(delete=False).name
        self.empty_config_path = NamedTemporaryFile(delete=False).name
        self.default_config_path = os.path.dirname(htrc.config.__file__)
        self.default_config_path = os.path.join(
            self.default_config_path, '.htrc.default')

        self.output_path = mkdtemp()
    
    @patch('htrc.config.bool_prompt')
    @patch('htrc.config.input')
    @patch('htrc.config.getpass')
    def test_credential_prompt(self, getpass_mock, input_mock, bool_mock):
        # configure mocks
        getpass_mock.return_value = '1234'
        input_mock.return_value = '1234'
        bool_mock.return_value = True

        # test prompts
        username, password = htrc.config.credential_prompt(self.config_path)
        self.assertEqual(username, '1234')
        self.assertEqual(password, '1234')

        # test read
        username, password = htrc.config.credentials_from_config(
            self.config_path)
        self.assertEqual(username, '1234')
        self.assertEqual(password, '1234')

    def test_empty_credential_exception(self):
        with self.assertRaises(EnvironmentError):
            htrc.config.credentials_from_config(self.empty_config_path)
