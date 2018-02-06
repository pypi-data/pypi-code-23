from __future__ import absolute_import, print_function, unicode_literals
import os
import subprocess
import unittest

from ..zip import zipfile

fullcontent = { 'one.txt': 'wibble\n', 'two.xml': 'bob\n' }
txtcontent = { 'one.txt': 'wibble\n' }

zipoutput = r'Archive:.*put\.zip\s+extracting: one\.txt\s+wibble\s+extracting: two\.xml\s+bob'


class testZipfile(unittest.TestCase):

    def setUp(self):
        self.local_dir = os.path.dirname(__file__)

    def tearDown(self):
        try:
            os.unlink(os.path.join(self.local_dir, 'put.zip'))
        except:
            pass

    def test_get(self):
        with open(os.path.join(self.local_dir, 'test.zip')) as zfh:
            zipcontent = zfh.read()

        zipobj = zipfile(zipcontent)

        content = zipobj.get()
        self.assertEquals(content, fullcontent)

        content = zipobj.get(pattern = r'.*\.txt')
        self.assertEquals(content, txtcontent)

    def test_put(self):
        zipobj = zipfile()
        zipcontent = zipobj.put('wibble\n', 'one.txt')
        zipcontent = zipobj.put('bob\n', 'two.xml')

        with open(os.path.join(self.local_dir, 'put.zip'), 'w') as zfh:
            zfh.write(zipcontent)

        output = subprocess.check_output(
            [ 'unzip', '-c', os.path.join(self.local_dir, 'put.zip') ]
        )
        self.assertRegexpMatches(output, zipoutput)

if __name__ == '__main__':
    unittest.main()
