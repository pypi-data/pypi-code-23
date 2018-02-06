from __future__ import absolute_import, print_function, unicode_literals
import os
import subprocess
import unittest

from ..local import local, TransferException

testfiles = { 'one.txt': 'wibble\n' }


class testLocal(unittest.TestCase):

    def setUp(self):
        self.local_dir = os.path.dirname(__file__)

    def tearDown(self):
        try:
            os.unlink(os.path.join(self.local_dir, 'local.test'))
        except:
            pass
        try:
            os.unlink(os.path.join(self.local_dir, 'newdir', 'local.test'))
        except:
            pass
        try:
            os.rmdir(os.path.join(self.local_dir, 'newdir'))
        except:
            pass

    def test_get(self):
        files = local(
            source = self.local_dir, debug = True
        ).get(
            r'.*\.txt'
        )
        self.assertEquals(files, testfiles)

    def test_get_nonexistant_directory(self):
        with self.assertRaises(TransferException):
            files = local(
                source = '/nope', debug = True
            ).get(
                r'.*\.txt'
            )

    def test_get_file_not_directory(self):
        with self.assertRaises(TransferException):
            files = local(
                source = __file__, debug = True
            ).get(
                r'.*\.txt'
            )

    def test_get_with_processed(self):
        with open(os.path.join(self.local_dir, 'local.test'), 'w') as outf:
            outf.write('')

        files = local(
            source = self.local_dir, processed = 'processed',
        ).get(
            r'.*\.test$'
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(self.local_dir, 'processed', 'local.test')
            )
        )
        os.unlink(os.path.join(self.local_dir, 'processed', 'local.test'))
        os.rmdir(os.path.join(self.local_dir, 'processed'))

    def test_get_with_delete(self):
        with open(os.path.join(self.local_dir, 'local.test'), 'w') as outf:
            outf.write('')

        files = local(
            source = self.local_dir,
        ).get(
            r'.*\.test$'
        )
        self.assertFalse(
            os.path.exists(
                os.path.join(self.local_dir, 'local.test')
            )
        )

    def test_put(self):
        local(
            destination = self.local_dir, debug = True
        ).put(
            'UNITTESTING!', 'local.test'
        )
        with open(os.path.join(self.local_dir, 'local.test')) as fh:
            self.assertEquals(fh.read(), 'UNITTESTING!')

    def test_put_nonexistant_directory(self):
        dstdir = os.path.join(self.local_dir, 'newdir')
        local(
            destination = dstdir, debug = True
        ).put(
            'UNITTESTING!', 'local.test'
        )
        with open(os.path.join(dstdir, 'local.test')) as fh:
            self.assertEquals(fh.read(), 'UNITTESTING!')

    def test_put_nopermissions(self):
        with self.assertRaises(TransferException):
            local(
                destination = '/nonexistant', debug = True,
            ).put(
                'UNITTESTING!', 'local.test'
            )

        with self.assertRaises(TransferException):
            local(
                destination = '/root', debug = True,
            ).put(
                'UNITTESTING!', 'local.test'
            )

if __name__ == '__main__':
    unittest.main()
