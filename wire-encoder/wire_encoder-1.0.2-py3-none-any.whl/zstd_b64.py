"""
An encoder and decoder that uses Zstandard and Base64
Leverage the content validation features of Zstandard
Dictionary feature is exposed, but details are left to the user
"""

from pybase64 import b64encode, b64decode
from zstd import ZstdCompressor, ZstdDecompressor, ZstdError
from .encoder import Encoder, Decoder
from .exceptions import InvalidData

# Note: The constructors don't like dict_data being None...


class ZstdBase64Encoder(Encoder):
    """
    An encoder that compresses with zstd, then encodes with base64
    """
    def __init__(self, level: int = 3, dict_data=None):
        """
        Constructor for the ZstdBase64Encoder
        :param level: The zstandard compression level.
        :param dict_data: Optional. Zstd custom dictionary data, see zstd doc
        """
        if dict_data:
            self.zstd = ZstdCompressor(level=level,
                                       dict_data=dict_data,
                                       write_checksum=True,
                                       write_content_size=True)
        else:
            self.zstd = ZstdCompressor(level=level,
                                       write_checksum=True,
                                       write_content_size=True)

    def encode(self, data: bytes) -> str:
        return b64encode(self.zstd.compress(data)).decode('utf8')


class ZstdBase64Decoder(Decoder):
    """
    A decoder that decodes base64 then decompresses with zstd
    :param dict_data: Optional. Zstd custom dictionary data, see zstd doc
    """
    def __init__(self, dict_data=None):
        if dict_data:
            self.zstd = ZstdDecompressor(dict_data=dict_data)
        else:
            self.zstd = ZstdDecompressor()

    def decode(self, data: str) -> bytes:
        try:
            return self.zstd.decompress(b64decode(data))
        except ZstdError:
            raise InvalidData("Invalid compression algorithm")
        except ValueError:
            raise InvalidData("Bad encoding")
