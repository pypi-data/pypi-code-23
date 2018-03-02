import binascii
import os

from contextlib import contextmanager

import zymkey

from .exceptions import CommandError


# https://github.com/oxplot/fysom/issues/1#issue-3668262
try:
    unicode = unicode
except NameError:  # 'unicode' is undefined, must be Python 3
    def is_string(buf):
        return isinstance(buf, str)
else:  # 'unicode' exists, must be Python 2
    def is_string(buf):
        return isinstance(buf, basestring)


def check_outfile(outfile):
    """
    Raise exception if the given outfile exists
    """
    if os.path.exists(outfile):
        raise CommandError('Outfile {} already exists'.format(outfile))


def get_random(num_bytes=512):
    """
    Generate a secret key

    Args:
        num_bytes (int): number of bytes to generate

    Returns (str):
        random hex string
    """
    _bytes = zymkey.client.get_random(num_bytes)

    return binascii.hexlify(_bytes)


@contextmanager
def open_with_perms(path, mode, perms):
    with open(path, mode) as fh:
        os.chmod(path, perms)

        yield fh


# http://stackoverflow.com/a/32107024/703144
class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
