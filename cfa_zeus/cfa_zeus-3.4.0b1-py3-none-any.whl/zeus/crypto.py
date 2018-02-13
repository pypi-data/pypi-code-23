#!/usr/bin/env python3
# coding: utf8
# -----------------------------------------------------------------
# zeus: crypto.py
#
# provide cryptograhic functions
#
# Copyright (C) 2016-2017, Christophe Fauchard
# -----------------------------------------------------------------
"""
Submodule: zeus.crypto

provide cryptograhic functions

Copyright (C) 2016-2017, Christophe Fauchard
"""

import os
import base64
import random
import zeus


class Vigenere():

    """
    Vigenere cipher

    can handle binary datas for both key and datas
    crypt datas are base64 coded for portability if not stored in files

    Required Parameters: None

    Optionnal Parameters:
    - string_key: key (utf8 string)
    - file_key: filename containing the key (any binary datas allowed)
    - gen_key: generate a random binary key in the file given (4096 bytes)

    """

    def __init__(self,
                 string_key=None,
                 file_key=None,
                 gen_key=None,
                 key_size=4096):

        if key_size is None:
            key_size = 4096
        self.key_size = key_size

        #
        # generate a key in the file given
        #
        if gen_key is not None:
            self.genkey(output_file=gen_key,
                        size=self.key_size)

        #
        # read key from a file
        #
        elif file_key is not None and os.path.exists(file_key):
            f = open(file_key, 'rb')
            self.key = f.read()
            f.close()

        #
        # key given as an utf8 string
        #
        elif string_key is not None:
            self.key = bytearray(string_key.encode('utf8'))

        #
        # try to read ZPK environment variable
        # (contain private key path)
        #
        elif os.environ.get("ZPK") is not None:
            f = open(os.environ.get("ZPK"), 'rb')
            self.key = f.read()
            f.close()

        #
        # else raise PrivateKeyException
        #
        else:
            raise zeus.exception.PrivateKeyException()

    """
    Parameters:
    - decrypted_datas: decrypted message (utf8 string)
    or filename containing datas
    (if datas are stored in a file, it can contain any binary datas)

    Optionnal parameters:
    - output_filename: file to write encrypted output base64 encoded
    """

    def encrypt(self,
                decrypted_datas,
                output_file=None):

        if os.path.exists(decrypted_datas):
            f = open(decrypted_datas, 'rb')
            self.decrypted_datas = f.read()
            f.close()
        else:
            self.decrypted_datas = bytearray(decrypted_datas.encode("utf8"))

        self.crypted_datas = bytearray(self.decrypted_datas)
        j = 0
        for i in range(0, len(self.decrypted_datas)):
            if j == len(self.key):
                j = 0
            self.crypted_datas[i] = (self.decrypted_datas[i] +
                                     self.key[j]) % 256
            j += 1

        self.crypted_datas = base64.b64encode(self.crypted_datas)

        if output_file is not None:
            f = open(output_file, 'wb')
            f.write(self.crypted_datas)
            f.close()

    """
    decrypting encrypted datas passed, update decrypted_datas attribute

    Parameters:
    - encrypted_datas: encrypted message (base64 encoded ascii string) or
    filename containing datas

    Optionnal parameters:
    - output_filename: file to write decrypted output

    Exceptions:
    - binascii.Error: if encrypted datas are not base64 encrypted,
    need import binascii
    """

    def decrypt(self,
                crypted_datas,
                output_file=None):

        if os.path.exists(crypted_datas):
            f = open(crypted_datas, 'rb')
            self.crypted_datas = bytearray(base64.b64decode(f.read()))
            f.close()
        else:
            self.crypted_datas = bytearray(
                base64.b64decode(crypted_datas.encode("utf8")))

        self.decrypted_datas = bytearray(self.crypted_datas)
        j = 0
        for i in range(0, len(self.crypted_datas)):
            if j == len(self.key):
                j = 0
            self.decrypted_datas[i] = (
                self.crypted_datas[i] - self.key[j]) % 256
            j += 1

        self.crypted_datas = base64.b64encode(self.crypted_datas)

        if output_file != None:
            f = open(output_file, 'wb')
            f.write(self.decrypted_datas)
            f.close()

    """
    generate random binary key, update the key attribute

    Optional parameters:
    - size: size of the key, default 4096 bytes
    - output_file: file to write the keys
    """

    def genkey(self,
               size,
               output_file=None):

        self.key = bytearray(size)
        for i in range(0, size):
            self.key[i] = random.getrandbits(8)

        if output_file is not None:
            f = open(output_file, 'wb')
            f.write(self.key)
            f.close()

    def get_key(self):
        return (self.key)

    def get_crypted_datas(self):
        return (self.crypted_datas)

    def get_decrypted_datas(self):
        return (self.decrypted_datas)

    def get_crypted_datas_base64(self):
        return (self.crypted_datas.decode("ascii"))

    def get_decrypted_datas_utf8(self):
        return (self.decrypted_datas.decode("utf8"))

    """
    print encrypted datas base64 coded
    """

    def __str__(self):
        if hasattr(self, 'crypted_datas'):
            return ((self.crypted_datas).decode("ascii"))
        else:
            return ("No crypted datas in buffer...")
