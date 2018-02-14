"""
An encoder and decoder that uses Zlib and Base85
While more wire efficient, it is significantly slower than base64 alternatives
"""

from base64 import b85encode, b85decode
from zlib import compress, decompress, error
from .encoder import Encoder, Decoder
from .exceptions import InvalidData


class ZlibBase85Encoder(Encoder):
    """
    An Encoder that compresses with zlib, then encodes with base85
    """
    def encode(self, data: bytes) -> str:
        return b85encode(compress(data)).decode('utf8')


class ZlibBase85Decoder(Decoder):
    """
    A Decoder that decodes base85, then decompresses the underlying zlib
    """
    def decode(self, data: str) -> bytes:
        try:
            return decompress(b85decode(data))
        except error:
            raise InvalidData("Invalid compression algorithm")
        except ValueError:
            raise InvalidData("Bad encoding")
