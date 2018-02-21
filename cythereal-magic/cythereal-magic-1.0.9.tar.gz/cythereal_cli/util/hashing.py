import hashlib


def hash_path(filepath, hashtype='sha1'):
    """ Hash a file at given path.

    Parameters
    ----------
    filepath: str
        Path to the file to be hashed
    hashtype: str
        Type of hash to create. Must be one of the hashes in `hashlib.algorithms`.
        Default is sha1.

    Returns
    -------
    str
        The hash of the file in hexadecimal format.

    """

    with open(filepath, 'rb') as infile:
        return hash_file(infile, hashtype=hashtype)


def hash_file(file_object, hashtype='sha1'):
    """ Hash a file-like object.

    File pointer is returned to front of file (file_object.seek(0,0) after hash
    is computed.

    Parameters
    ----------
    file_object: File
        File like object that supports read() with chunk size as well as seek().
    hashtype: str
        Type of hash to create. Must be one of the hashes in `hashlib.algorithms`.
        Default is sha1.

    Returns
    -------
    str
        The hash of the file in hexadecimal format.

    """

    hash_func = getattr(hashlib, hashtype.lower())
    digest = hash_func()
    while True:
        block = file_object.read(2**10)  # Magic number: one-megabyte blocks.
        if not block:
            break
        digest.update(block)
    file_object.seek(0, 0)
    return digest.hexdigest()


def hash_string(string_contents, hashtype='sha1'):
    """ Hash a string with the specified hash function.
    Parameters
    ----------
    string_contents: str
        String to hash.
    hashtype: str
        Type of hash to create. Must be one of the hashes in `hashlib.algorithms`.
        Default is sha1.

    Returns
    -------
    str
        The hash of the file in hexadecimal format.

    """
    hash_func = getattr(hashlib, hashtype.lower())
    digest = hash_func()
    digest.update(string_contents)
    return digest.hexdigest()
