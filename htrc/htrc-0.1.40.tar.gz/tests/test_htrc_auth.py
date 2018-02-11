from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

from io import BytesIO  # used to stream http response into zipfile.
import sys
from tempfile import NamedTemporaryFile, mkdtemp
import unittest2 as unittest

import htrc.auth

# Import mock tests
if sys.version_info.major == 2:
    from mock import Mock, patch, PropertyMock
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch, PropertyMock


class MockResponse(BytesIO):
    def __init__(self, data, status=200, *args, **kwargs):
        BytesIO.__init__(self, data, *args, **kwargs)
        self.status = status

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.config_path = NamedTemporaryFile(delete=False).name
        self.empty_config_path = NamedTemporaryFile(delete=False).name

        self.output_path = mkdtemp()

    def tearDown(self):
        import os, shutil
        os.remove(self.config_path)
        shutil.rmtree(self.output_path)

    @patch('htrc.volumes.http.client.HTTPSConnection')
    def test_get_oauth2_token(self, https_mock):
        response_mock = Mock(status=200, return_value=b'')
        response_mock.read.return_value =\
            '{"access_token": "a1b2c3d4e5f6"}'.encode('utf8')
        https_mock.return_value.getresponse.return_value = response_mock

        #token = htrc.volumes.get_oauth2_token('1234','1234')
        #self.assertEqual(token, 'a1b2c3d4e5f6')

    @patch('htrc.volumes.http.client.HTTPSConnection')
    def test_get_oauth2_token_error(self, https_mock):
        response_mock = Mock(status=500)
        https_mock.return_value.getresponse.return_value = response_mock

        #with self.assertRaises(EnvironmentError):
        #    token = htrc.volumes.get_oauth2_token('1234','1234')

