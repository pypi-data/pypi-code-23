from datetime import datetime
from fnmatch import fnmatch
from os.path import basename


def age(min_age):
    """Create a filter that tests if the file's mtime is ``min_age`` old.
    """
    return lambda file_: file_.mtime <= datetime.now() - min_age


def glob(pattern):
    """Create a filter that tests if the file's name matches ``pattern``.
    """
    return lambda file_: fnmatch(basename(file_.path), pattern)


def negate(filter_):
    """Create a filter that negates another filter result.
    """
    return lambda file_: not filter_(file_)
