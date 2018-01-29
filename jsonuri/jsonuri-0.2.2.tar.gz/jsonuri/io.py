import gzip
import base64


def compress(data):
    """
    Compresses a string (or bytes) using Gzip and returns its Base64 representation

    :param data: string or bytes
    :return: Base64 (bytes) representation of compressed data
    """

    if isinstance(data, bytes):
        source = data
    elif isinstance(data, str):
        source = bytes(data, encoding='utf-8')
    else:
        raise RuntimeError("Compression is only supported for strings and bytes")

    return base64.b64encode(gzip.compress(source))


def decompress(data):
    """
    Decodes a Base64 bytes (or string) input and decompresses it using Gzip
    :param data: Base64 (bytes) data to be decoded
    :return: Decompressed and decoded bytes
    """

    if isinstance(data, bytes):
        source = data
    elif isinstance(data, str):
        source = bytes(data, encoding='utf-8')
    else:
        raise RuntimeError("Compression is only supported for strings and bytes")

    return gzip.decompress(base64.b64decode(source))
