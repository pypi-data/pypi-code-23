"""
Utilities for exchanging keys and secrets within GPG.

Copyright 2018 Leon Helwerda

GPP exchange is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

GPG exchange is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <https://www.gnu.org/licenses/>.
"""

import os
import gpg

class Exchange(object):
    """
    GPG exchange service.
    """

    def __init__(self, armor=True, home_dir=None, passphrase=None):
        self._gpg = gpg.Context(armor=armor)

        if home_dir is not None:
            self._gpg.home_dir = home_dir

        if passphrase is not None:
            self._passphrase = passphrase
            self._gpg.pinentry_mode = gpg.constants.PINENTRY_MODE_LOOPBACK
            self._gpg.set_passphrase_cb(passphrase)
        else:
            self._passphrase = None

    def generate_key(self, name, email, comment='exchange generated key',
                     passphrase=None):
        """
        Generate a new key pair for the given `name` and `email`, including
        a `comment`. Either `passphrase` must provide a passphrase string or
        the passphrase callback is used, otherwise a `RuntimeError` is raised.

        Returns the Key object of the newly generated key.
        """

        if passphrase is None:
            if self._passphrase is not None:
                passphrase = self._passphrase(name, comment, 0, None)
            else:
                raise RuntimeError('Must provide a passphrase to generate key')

        self._gpg.op_genkey("""<GnupgKeyParms format="internal">
Key-Type: default
Subkey-Type: default
Name-Real: {name}
Name-Comment: {comment}
Name-Email: {email}
Expire-Date: 0
Passphrase: {passphrase}
</GnupgKeyParms>""".format(name=name, email=email, comment=comment,
                           passphrase=passphrase), None, None)

        return self._gpg.op_genkey_result()

    def find_key(self, pattern):
        """
        Retrieve the key object that matches the string `pattern`.

        Returns the Key object or raises a `KeyError`.
        """

        try:
            return self._gpg.keylist(pattern).next()
        except StopIteration:
            raise KeyError(pattern)

    def delete_key(self, pattern, secret=False):
        """
        Remove the key that matches the string `pattern`.

        Returns the deleted Key object or raises a `KeyError`.
        """

        key = self.find_key(pattern)
        flags = gpg.constants.DELETE_FORCE
        if secret:
            flags |= gpg.constants.DELETE_ALLOW_SECRET

        self._gpg.op_delete_ext(key, flags)
        return key

    def _get_imported_key(self, import_result):
        try:
            fpr = import_result.imports[0].fpr
            return self.find_key(fpr)
        except (KeyError, IndexError, AttributeError) as error:
            raise ValueError(str(error), import_result)

    def import_key(self, pubkey):
        """
        Import a single public key provided in the string `pubkey`.

        Returns a tuple of the imported key object and the import result object.
        If not exactly one key is provided or imported, then a `ValueError` is
        raised with the import result in its arguments.
        """

        with gpg.Data(pubkey) as import_key:
            result = self._gpg.op_import(import_key)

        if result.considered != 1:
            raise ValueError('Exactly one public key must be provided', result)
        if result.imported != 1:
            raise ValueError('Given public key must be valid', result)

        return self._get_imported_key(result), result

    def export_key(self, pattern):
        """
        Export the public key part of the matching the pattern provided in the
        string `pattern`.

        The key is returned as a string.
        """

        with gpg.Data() as export_key:
            self._gpg.op_export(pattern, 0, export_key)
            return self._read_data(export_key)

    @staticmethod
    def _read_data(data):
        data.seek(0, os.SEEK_SET)
        return data.read()

    def _encrypt(self, plaintext, ciphertext, recipients, always_trust):
        if recipients is None:
            recipients = []
        elif not isinstance(recipients, (list, tuple)):
            recipients = [recipients]

        self._gpg.encrypt(plaintext, recipients, sink=ciphertext,
                          always_trust=always_trust)

    def encrypt_text(self, data, recipients=None, always_trust=False):
        """
        Encrypt the plain text `data` for the given `recipients`, which may be
        a single Key object, a list of Key objects, or `None` to encrypt the
        data symmetrically.

        If `always_trust` is `True` then keys in the recipients that are not
        explicitly marked as trusted are still allowed.

        The encrypted data is returned as a string.
        """

        with gpg.Data(data) as plaintext:
            with gpg.Data() as ciphertext:
                self._encrypt(plaintext, ciphertext, recipients, always_trust)
                return self._read_data(ciphertext)

    def encrypt_file(self, input_file, output_file, recipients=None, always_trust=False):
        """
        Encrypt the plain text stored in `input_file` for the given `recipients`
        and store the encrypted data in `output_file`. The files must be already
        opened with the correct read/write (and binary) modes. The recipients
        may be a single Key object, a list of Key objects, or `None` to encrypt
        the data symmetrically.

        If `always_trust` is `True` then keys in the recipients that are not
        explicitly marked as trusted are still allowed.
        """

        with gpg.Data() as plaintext:
            plaintext.new_from_fd(input_file)
            with gpg.Data() as ciphertext:
                ciphertext.new_from_fd(output_file)
                self._encrypt(plaintext, ciphertext, recipients, always_trust)

    def _decrypt(self, ciphertext, plaintext):
        try:
            self._gpg.decrypt(ciphertext, plaintext)
        except gpg.errors.GPGMEError as error:
            if error.getcode() == gpg.errors.NO_DATA:
                raise ValueError('No encrypted data')

            raise

    def decrypt_text(self, data):
        """
        Decrypt the ciphertext `data`.

        The decrypted data is returned as a string.
        """

        with gpg.Data() as sink:
            self._decrypt(data, sink)
            return self._read_data(sink)

    def decrypt_file(self, input_file, output_file):
        """
        Decrypt the ciphertext stored in `input_file` and store the decrypted
        data in `output_file`. The files must be already opened with the correct
        read/write and binary modes.
        """

        with gpg.Data() as ciphertext:
            ciphertext.new_from_fd(input_file)
            with gpg.Data() as plaintext:
                plaintext.new_from_fd(output_file)
                self._decrypt(ciphertext, plaintext)
