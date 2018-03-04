
from __future__ import print_function
import os
import sys

MDB_VERSION = "0.3.13"
__interactive__ = os.isatty(sys.stdout.fileno())

def eprint(*args, **kwargs):
    # If not interactive (e.g. writing to log), show user from whence msg came
    if not __interactive__:
        print('mdbtools Error: ', file=sys.stderr, end='')
    abort = kwargs.pop("abort", None)
    print(*args, file=sys.stderr, **kwargs)
    if abort:
        sys.exit(abort)

def mprint(*args, **kwargs):
    # If not interactive (e.g. writing to log), show user from whence msg came
    if not __interactive__:
        print('mdbtools: ', file=sys.stdout, end='')
    print(*args, file=sys.stdout, **kwargs)
