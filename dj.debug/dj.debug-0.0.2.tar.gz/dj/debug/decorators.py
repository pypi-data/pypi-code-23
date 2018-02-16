
import functools
import time

from .sql import debug_sql


def debug(f):

    @functools.wraps(f)
    def wrap(*args, **kwargs):
        start = time.time()
        with debug_sql():
            result = f(*args, **kwargs)
        print "total time taken %ss" % (time.time() - start)
        return result
    return wrap
