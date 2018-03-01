import base64

try:
    from hashlib import blake2b
except ImportError:
    from pyblake2 import blake2b

from hashlib import sha512


def get_digests(file_stream):
    """Get digests function.

    :param file_stream: Takes a file stream.
    :return: a dictionary of hashes associated with the data.
    """
    # Hash the file stream using sha-512
    # As a redundancy include blake2
    sha_h = sha512()
    blake_h = blake2b()

    b_file_stream = base64.b64encode(file_stream.encode())

    sha_h.update(b_file_stream)
    blake_h.update(b_file_stream)

    # return a digest of the hash
    sha_digest = sha_h.hexdigest()
    blake2_digest = blake_h.hexdigest()

    return {
        'sha256': sha_digest,
        'blake2': blake2_digest
    }
