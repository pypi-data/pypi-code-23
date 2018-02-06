from __future__ import absolute_import, print_function, unicode_literals
import unittest
try:
    from mock import Mock, patch, ANY
except ImportError:
    from unittest.mock import Mock, patch, ANY

from ..ftp import ftp, TransferException

class testFTP(unittest.TestCase):

    test_data = 'eonfeoiwnfioenmfoieapow kjpojfwpfwdfls;DL'

    def setUp(self):
        patcher = patch('ftplib.FTP', autospec = True)

        def mock_retrbinary(cmd, func):
            func(self.test_data)

        def mock_storbinary(cmd, stringio): # can't seem to mock StringIO :/
            self.ret_data = stringio.getvalue()

        self.mock_ftp = patcher.start().return_value
        self.mock_ftp.nlst = Mock(return_value = [ 'test.xml', 'test.txt' ])
        self.mock_ftp.retrbinary = Mock(side_effect = mock_retrbinary)
        self.mock_ftp.storbinary = Mock(side_effect = mock_storbinary)

        self.addCleanup(patcher.stop)

        self.ret_data = ''

    def test_get(self):
        obj = ftp('local.test', 'user1', 'passwd')
        contents = obj.get(r'.*\.xml')

        self.mock_ftp.connect.assert_called_with('local.test', 21, 30)
        self.mock_ftp.login.assert_called_with('user1', 'passwd')

        self.assertIn('test.xml', contents)
        self.assertNotIn('test.txt', contents)
        self.assertEquals(self.test_data, contents[ 'test.xml' ])

    def test_get_with_processed(self):
        obj = ftp('local.test', None, None, processed = 'done')
        contents = obj.get()

        self.mock_ftp.rename.assert_any_call('test.xml', 'done/test.xml')
        self.mock_ftp.rename.assert_any_call('test.txt', 'done/test.txt')

    def test_put(self):
        obj = ftp('local.test', 'user1', 'passwd')
        obj.put(self.test_data, 'test.txt')

        self.mock_ftp.connect.assert_called_with('local.test', 21, 30)
        self.mock_ftp.login.assert_called_with('user1', 'passwd')
        self.mock_ftp.storbinary.assert_called_with(
            'STOR ./test.txt.uploading', ANY
        )
        self.assertEqual(self.ret_data, self.test_data)
        self.mock_ftp.rename.assert_called_with(
            './test.txt.uploading', './test.txt'
        )

    def test_put_no_rename(self):
        obj = ftp('local.test', 'user1', 'passwd')
        obj.put(self.test_data, 'test.txt', rename = False)

        self.mock_ftp.storbinary.assert_called_with(
            'STOR ./test.txt', ANY
        )
        self.assertEqual(self.ret_data, self.test_data)
        self.assertEqual(self.mock_ftp.rename.call_count, 0)

    def test_connection_error(self):
        self.mock_ftp.connect = Mock(side_effect = Exception('wibble'))

        obj = ftp('local.test', None, None)
        with self.assertRaises(TransferException):
            obj.put(None, '')

if __name__ == '__main__':
    unittest.main()
