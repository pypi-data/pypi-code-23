# -*- coding: utf-8 -*-
"""icemicro module
"""
from iceman.crypto_strategies.strategy import Strategy

class Null(Strategy):

    """Null Strategy implementation

    :param preshared_key: symmetric encryption key
    :type preshared_key: str
    """
    def __init__(self, preshared_key): # pylint: disable=unused-argument
        self.cipher_suite = None

    def encrypt(self, payload):
        """encrypts a given payload

        :param payload: the string to encrypt
        :type payload: str

        :returns: str -- the original string
        """
        return payload

    def decrypt(self, token):
        """decrypts a given token

        :param token: the token to decrypt
        :type token: str

        :returns: str -- the token
        """
        return token
