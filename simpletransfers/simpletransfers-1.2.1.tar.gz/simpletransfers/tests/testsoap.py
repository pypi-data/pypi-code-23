from __future__ import absolute_import, print_function, unicode_literals
import unittest
try:
    from mock import Mock, patch, ANY
except ImportError:
    from unittest.mock import Mock, patch, ANY
from suds import WebFault
from urllib2 import URLError

from ..soap import soap, TransferException


class testSOAP(unittest.TestCase):

    test_data = 'eonfeoiwnfioenmfoieapow kjpojfwpfwdfls;DL'

    def setUp(self):
        patcher = patch('suds.client.Client', autospec = True)

        self.mock_soap_constructor = patcher.start()
        self.mock_soap = self.mock_soap_constructor.return_value
        self.mock_soap.service = Mock()
        self.mock_soap.service.RemoteFunctionName = Mock(
            return_value = self.test_data
        )

        self.addCleanup(patcher.stop)

    def test_get(self):
        obj = soap('local.test')
        contents = obj.get('RemoteFunctionName')

        self.mock_soap_constructor.assert_called_with(
            'local.test', timeout = 10
        )
        self.mock_soap.service.RemoteFunctionName.assert_called_with(None)

        self.assertEquals(self.test_data, contents)

    def test_with_headers(self):
        obj = soap('local.test', headers = self.test_data)
        self.mock_soap.set_options.assert_called_with(
            soapheaders = self.test_data
        )

    def test_put(self):
        obj = soap('local.test')
        contents = obj.put(self.test_data, 'RemoteFunctionName')

        self.mock_soap.service.RemoteFunctionName.assert_called_with(
            self.test_data
        )
        self.assertEquals(self.test_data, contents)

    def test_unrecognised_method(self):
        del self.mock_soap.service.RemoteFunctionName
        obj = soap('local.test')

        with self.assertRaises(TransferException):
            obj.get('RemoteFunctionName')

    def test_method_error(self):
        self.mock_soap.service.RemoteFunctionName.side_effect =\
            WebFault(None, None)
        obj = soap('local.test')

        with self.assertRaises(TransferException):
            obj.get('RemoteFunctionName')

    def test_method_timeout(self):
        self.mock_soap.service.RemoteFunctionName.side_effect =\
            URLError('timed out')
        obj = soap('local.test')

        self.assertEquals(obj.get('RemoteFunctionName'), None)

if __name__ == '__main__':
    unittest.main()
