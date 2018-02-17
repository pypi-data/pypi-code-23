#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import not_none
from hamcrest import is_

import shutil
import os
import unittest
import tempfile

import fudge

import zc.buildout.buildout
import zc.buildout.testing

from nti.recipes.passwords import DecryptFile
from nti.recipes.passwords import DecryptSection
from nti.recipes.passwords import _BaseFormat as BaseFormat


NoDefaultBuildout = zc.buildout.testing.Buildout


class TestDecrypt(unittest.TestCase):

    assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                unittest.TestCase.assertRaisesRegexp)

    def setUp(self):
        tempdir = tempfile.mkdtemp('passwords_test')
        self.addCleanup(shutil.rmtree, tempdir)
        self.old_dir = os.getcwd()
        os.chdir(tempdir)
        os.mkdir('parts')


    def tearDown(self):
        os.chdir(self.old_dir)

    def test_no_file(self):
        # No verification, just sees if it runs
        buildout = NoDefaultBuildout()
        DecryptSection(buildout, 'passwords', {'base_passwd': ''})
        # buildout.print_options()

    @fudge.patch('getpass.getpass')
    def test_decrypt_data_section(self, mock_getpass):

        ciphertext = (b'Salted__\xbe\x82\x11\xc4\x01\xe6\x94\xfc\x93\xb5\x8aF\xeb\x8chEy"'
                      b'\xd0\xb4\x04\xf3g\xb3.UX\x18\x17\x95\xe7 x7\x16\xa4{\x805~z\xe5\xad\xdc\xc4\xdc'
                      b'\xd43\x8e\xfd\xda\x108\xbfv\xf8yW\x1f\xd2\xd73j\x0f\xce\x0f(4\x95\xe3{&~{\xdf'
                      b'\x8ekm\xbb\x01\x17\xf28\x97\xd4\xfaSL\x99\xb5I\xfb\xc4\t\xb8\xeeH\x97\x02\\\xc8\xd6dw')

        fd, cast_file_path = tempfile.mkstemp(suffix=".cast5", prefix="passwords_test")
        self.addCleanup(os.remove, cast_file_path)
        os.write(fd, ciphertext)
        os.close(fd)

        mock_getpass = mock_getpass.is_callable().times_called(1)
        mock_getpass.returns('temp001')

        buildout = NoDefaultBuildout()
        options = {
            'file': cast_file_path,
        }

        section = DecryptSection(buildout, 'passwords', options)

        assert_that(options, has_entry('_input_mod_time', not_none()))
        assert_that(options, has_entry('sql_passwd', 'rdstemp001'))

        section.install()

        assert_that(os.path.isfile(os.path.join('parts', 'passwords', 'plaintext')))
        assert_that(os.path.isfile(os.path.join('parts', 'passwords', 'checksum')))

        # Doing it again is a no-op
        options = {
            'file': cast_file_path,
        }

        DecryptSection(buildout, 'passwords', options)
        # Now make the data bad
        with open(cast_file_path, 'wb') as f:
            f.write(b'NOT GOOD')

        with self.assertRaisesRegex(Exception,
                                    "Improper input file format"):
            DecryptSection(buildout, 'passwords', options)

    def test_wrong_filename(self):
        buildout = NoDefaultBuildout()
        options = {
            'file': 'foo.txt',
        }

        with self.assertRaisesRegex(Exception,
                                    "Input is not a .cast5 file"):
            DecryptSection(buildout, 'passwerds', options)

    def test_missing_file(self):
        buildout = NoDefaultBuildout()
        options = {
            'file': 'foo.cast5',
        }

        with self.assertRaisesRegex(Exception,
                                    "Input file '.*foo.cast5' does not"):
            DecryptSection(buildout, 'passwerds', options)

    @fudge.patch('getpass.getpass')
    def test_decrypt_data_file(self, mock_getpass):

        ciphertext = (b'Salted__\xbe\x82\x11\xc4\x01\xe6\x94\xfc\x93\xb5\x8aF\xeb\x8chEy"'
                      b'\xd0\xb4\x04\xf3g\xb3.UX\x18\x17\x95\xe7 x7\x16\xa4{\x805~z\xe5\xad\xdc\xc4\xdc'
                      b'\xd43\x8e\xfd\xda\x108\xbfv\xf8yW\x1f\xd2\xd73j\x0f\xce\x0f(4\x95\xe3{&~{\xdf'
                      b'\x8ekm\xbb\x01\x17\xf28\x97\xd4\xfaSL\x99\xb5I\xfb\xc4\t\xb8\xeeH\x97\x02\\\xc8\xd6dw')

        fd, cast_file_path = tempfile.mkstemp(suffix=".cast5", prefix="passwords_test")
        self.addCleanup(os.remove, cast_file_path)
        os.write(fd, ciphertext)
        os.close(fd)

        mock_getpass.is_callable().returns('temp001')

        buildout = NoDefaultBuildout()
        options = {
            'file': cast_file_path,
            'output-file': 'decrypted'
        }

        section = DecryptFile(buildout, 'passwords', options)

        assert_that(options, has_entry('_input_mod_time', not_none()))

        section.install()

        assert_that(os.path.isfile(os.path.join('parts', 'passwords', 'plaintext')))
        assert_that(os.path.isfile(os.path.join('parts', 'passwords', 'checksum')))
        assert_that(os.path.isfile('decrypted'))

        with open('decrypted', 'rb') as f:
            data = f.read()

        self.assertIn(b'[passwords]', data)

class TestEncrypt(unittest.TestCase):

    # Encryption is not actually used by this package,
    # I don't know why it's there, mostly for symmetry I guess.

    def test_cipher(self):

        f = BaseFormat()
        # Carefully choose the plaintext to be a mulitple of the block size
        b = f.make_ciphertext(u'passphrase', u'plaintex')
        assert_that(b, is_(bytes))
