#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recipes to decrypt and encrypt passwords and related data.

See http://ejohn.org/blog/keeping-passwords-in-source-control/

File Format
===========

We are duplicating the OpenSSL file format, which is reverse engineered to be
the following::

  'Salted__' + ........ + ciphertext

where ``........`` is the 8 byte salt. The 16-byte key and 8 byte IV are
derived from the passphrase combined with the salt (the IV is not stored
in the file)::

  Key = MD5( passphrase + salt )
  IV  = MD5( key + passphrase + salt )[:8]

That is, the key is the MD5 checksum of concatenating the passphrase
followed by the salt, and the initial vector is the first 8 bytes of the
MD5 of the key, passphrase and salt concatenated.

"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from io import StringIO
import os

import zc.buildout

try:
    from configparser import ConfigParser
except ImportError: # Python 2 pragma: no cover
    from ConfigParser import SafeConfigParser as ConfigParser

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.ciphers.algorithms import CAST5

CAST_BLOCK_SIZE = 8 # This is fixed

import getpass
from hashlib import md5


class _BaseFormat(object):
    _salt = None

    @property
    def salt(self):
        "Eight bytes of random salt data"
        if self._salt is None:
            self._salt = self.new_salt()
        return self._salt

    def new_salt(self):
        return os.urandom(CAST_BLOCK_SIZE)

    def make_key(self, passphrase):
        if not isinstance(passphrase, bytes):
            passphrase = passphrase.encode("utf-8")
        salt = self.salt
        assert isinstance(salt, bytes) and len(salt) == 8, salt

        return md5(passphrase + salt).digest()

    def make_iv(self, passphrase):
        key = self.make_key(passphrase)
        if not isinstance(passphrase, bytes):
            passphrase = passphrase.encode('utf-8')
        return md5(key + passphrase + self.salt).digest()[:8]

    def _make_cipher(self, passphrase):
        key = self.make_key(passphrase)
        iv = self.make_iv(passphrase)
        cipher = Cipher(CAST5(key), CBC(iv), backend=default_backend())
        return cipher

    def make_ciphertext(self, passphrase, plaintext):
        if not isinstance(plaintext, bytes):
            plaintext = plaintext.encode('utf-8')
        encryptor = self._make_cipher(passphrase).encryptor()
        return encryptor.update(plaintext) + encryptor.finalize()

    def get_plaintext(self, passphrase, ciphertext):
        decryptor = self._make_cipher(passphrase).decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()


class _EncryptedFile(_BaseFormat):

    def __init__(self, name):
        self.name = name
        with open(name, 'rb') as f:
            self._data = f.read()
        if not self._data.startswith(b'Salted__'):
            raise zc.buildout.UserError("Improper input file format")

    @property
    def checksum(self):
        # In a format just like the md5sum command line
        # program. Must be a native string
        csum = md5(self._data).hexdigest()
        basename = os.path.basename(self.name)
        return csum + '  ' + basename + '\n'

    @property
    def salt(self):
        return self._data[8:16]

    @property
    def ciphertext(self):
        return self._data[16:]


class _BaseDecrypt(object):

    needs_write = False
    plaintext = None
    part_dir = None
    checksum_file = ''
    plaintext_file = ''

    def __init__(self, buildout, name, options):
        # Allow no file to be able to specify defaults
        # for developers; obviously production must have
        # the real things
        if not options.get('file'):
            return

        input_file = options['file']
        if not input_file.endswith('.cast5'):
            raise zc.buildout.UserError("Input is not a .cast5 file")

        input_file = os.path.abspath(input_file)
        if not os.path.isfile(input_file):
            msg = "Input file '%s' does not exist" % input_file
            raise zc.buildout.UserError(msg)

        stat = os.stat(input_file)
        options['_input_mod_time'] = repr(stat.st_mtime)

        self._encrypted_file = _EncryptedFile(input_file)
        options['_checksum'] = self._encrypted_file.checksum

        self.part_dir = os.path.join(buildout['buildout']['parts-directory'],
                                     name)

        self.checksum_file = os.path.join(self.part_dir, 'checksum')
        self.plaintext_file = os.path.join(self.part_dir, 'plaintext')

        old_checksum = None
        self.plaintext = None
        if os.path.exists(self.checksum_file):
            with open(self.checksum_file, 'r') as f:
                old_checksum = f.read()

        if (old_checksum != self._encrypted_file.checksum
                or not os.path.exists(self.plaintext_file)):
            passphrase = getpass.getpass('Password for ' + name + ': ')

            self.plaintext = self._encrypted_file.get_plaintext(passphrase,
                                                                self._encrypted_file.ciphertext)
            # Cast5 CBC is a block cipher with an 8-byte block size.
            # The plaintext is always padded to be a multiple of 8
            # bytes by OpenSSL. If one byte is required, the padding
            # is \x01. If two bytes, \x02\x02, three bytes
            # \x03\x03\x03 and so on. If no bytes were required
            # because the input was the perfect size, then an entire
            # block of \x08 is added, so there is always padding to
            # remove.
            for pad in (chr(i) * i for i in range(8, 0, -1)):
                pad = pad.encode("utf-8")
                if self.plaintext.endswith(pad):
                    self.plaintext = self.plaintext[:-len(pad)]
                    break
            self.needs_write = True

        if self.plaintext is None:
            with open(self.plaintext_file, 'rb') as f:
                self.plaintext = f.read()

    def _do_write(self):
        if self.part_dir and not os.path.isdir(self.part_dir):
            os.mkdir(self.part_dir, 0o2770)

        if self.needs_write:
            with open(self.plaintext_file, 'wb') as f:
                f.write(self.plaintext)

            with open(self.checksum_file, 'w') as f:
                f.write(self._encrypted_file.checksum)

        return self.checksum_file, self.plaintext_file

    def install(self):
        return self._do_write()
    update = install


class DecryptSection(_BaseDecrypt):

    @classmethod
    def text_(cls, s):
        return s.decode("utf-8") if isinstance(s, bytes) else s

    def __init__(self, buildout, name, options):
        _BaseDecrypt.__init__(self, buildout, name, options)
        if self.plaintext:
            config = ConfigParser()
            source = self.text_(self.plaintext)
            read = getattr(config, 'read_file', config.readfp)
            read(StringIO(source))
            for key, value in config.items(name):
                options[key] = str(value)


class DecryptFile(_BaseDecrypt):

    def __init__(self, buildout, name, options):
        self.output_file = options['output-file']  # validate before we decrypt
        _BaseDecrypt.__init__(self, buildout, name, options)

    def _do_write(self):
        base_files = super(DecryptFile, self)._do_write()
        if self.needs_write:
            with open(self.output_file, 'wb') as f:
                f.write(self.plaintext)
        return base_files + (self.output_file,)
