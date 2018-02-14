"""
An encoder and decoder that uses Zlib and Base64
"""

from zlib import compress, decompress, error
from pybase64 import b64encode, b64decode
from .encoder import Encoder, Decoder
from .exceptions import InvalidData


class ZlibBase64Encoder(Encoder):
    """
    An encoder that uses zlib and base64
    """
    def __init__(self):
        pass

    def encode(self, data: bytes) -> str:
        return b64encode(compress(data)).decode('utf8')


class ZlibBase64Decoder(Decoder):
    """
    A Decoder that uses zlib and base85
    """
    def __init__(self):
        pass

    def decode(self, data: str) -> bytes:
        try:
            return decompress(b64decode(data))
        except error:
            raise InvalidData("Invalid compression algorithm")
        except ValueError:
            raise InvalidData("Bad encoding")
