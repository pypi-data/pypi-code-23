from __future__ import absolute_import, print_function, unicode_literals
import unittest
from mock import Mock, patch, ANY

from ..sftp import sftp, TransferException


class testSFTP(unittest.TestCase):

    test_data = 'eonfeoiwnfioenmfoieapow kjpojfwpfwdfls;DL'

    def setUp(self):
        trans_patcher = patch('paramiko.Transport', autospec = True)
        conn_patcher = patch('paramiko.SFTPClient', autospec = True)

        self.mock_transport_constructor = trans_patcher.start()
        self.mock_transport = self.mock_transport_constructor.return_value
        self.mock_sftp = conn_patcher.start().from_transport(self.mock_transport)

        self.mock_sftp.listdir = Mock(
            return_value = [ 'test.xml', 'test.txt' ]
        )
        self.mock_file = Mock()
        self.mock_file.read = Mock(return_value = self.test_data)
        self.mock_sftp.file = Mock(return_value = self.mock_file)

        self.addCleanup(conn_patcher.stop)
        self.addCleanup(trans_patcher.stop)

    def test_get(self):
        obj = sftp('local.test', 'user1', 'passwd')
        contents = obj.get(r'.*\.xml')

        self.mock_transport_constructor.assert_called_with('local.test:22')
        self.mock_transport.connect.assert_called_with(
            username = 'user1', password = 'passwd'
        )
        self.mock_sftp.file.assert_called_with('./test.xml', 'rb')

        self.assertIn('test.xml', contents)
        self.assertNotIn('test.txt', contents)
        self.assertEquals(self.test_data, contents[ 'test.xml' ])

    def test_get_with_processed(self):
        obj = sftp('local.test', None, None, processed = 'done')
        contents = obj.get()

        self.mock_sftp.rename.assert_any_call('./test.xml', 'done/test.xml')
        self.mock_sftp.rename.assert_any_call('./test.txt', 'done/test.txt')

    def test_put(self):
        obj = sftp('local.test', 'user1', 'passwd', permissions = 0o777)
        obj.put(self.test_data, 'test.txt')

        self.mock_transport_constructor.assert_called_with('local.test:22')
        self.mock_transport.connect.assert_called_with(
            username = 'user1', password = 'passwd'
        )

        self.mock_sftp.file.assert_called_with('./test.txt.uploading', 'wb')
        self.mock_file.write.assert_called_with(self.test_data)

        self.mock_sftp.rename.assert_called_with(
            './test.txt.uploading', './test.txt'
        )

    def test_put_no_rename(self):
        obj = sftp('local.test', 'user1', 'passwd')
        obj.put(self.test_data, 'test.txt', rename = False)

        self.mock_sftp.file.assert_called_with(
            './test.txt', 'wb'
        )
        self.mock_file.write.assert_called_with(self.test_data)
        self.assertEqual(self.mock_sftp.rename.call_count, 0)

    def test_connection_error(self):
        self.mock_transport.connect = Mock(
            side_effect = Exception('wibble')
        )

        obj = sftp('local.test', None, None)
        with self.assertRaises(TransferException):
            obj.put(None, '')

if __name__ == '__main__':
    unittest.main()
