import hashlib


def md5(string):
    """Returns the md5 hash of a string

    Args:
        string (str) any string

    Returns: (str) the md5 hash
    """
    return hashlib.md5(string.encode('utf-8')).hexdigest()
