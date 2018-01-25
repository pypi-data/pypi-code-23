"""
where the helpers go
"""
import datetime
import errno
import os


def js_ts_to_str(_timestamp):
    """returns a nice date string from a js timestamp"""
    return datetime.datetime.fromtimestamp(
        _timestamp / 1000
    ).strftime('%Y-%m-%d %H:%M:%S')


def mkdir(path):
    """creates a folder if it doesnt exist"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
