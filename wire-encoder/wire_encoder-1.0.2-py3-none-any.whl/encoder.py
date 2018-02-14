"""
Simple encoder and decoder interfaces for wire safe encoding
"""

from abc import ABCMeta, abstractmethod


class Encoder(metaclass=ABCMeta):
    """
    An Encoder provides facilities to encode some data
    Encoding format is defined by the actual implementation
    """

    @abstractmethod
    def encode(self, data: bytes) -> str:
        """
        Encode the provided bytes into the given data format.
        :param data: The data to be encoded
        :return: A string that should be wire safe
        """
        pass


class Decoder(metaclass=ABCMeta):
    """
    A Decoder provides facilities to decode some data
    Decoding format is defined by the actual implementation
    """

    @abstractmethod
    def decode(self, data: str) -> bytes:
        """
        Decode the provided string from the given data format into bytes
        :param data: The wire safe string
        :return: The decoded bytes
        """
        pass
