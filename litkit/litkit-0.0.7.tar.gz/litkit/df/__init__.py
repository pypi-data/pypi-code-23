import hashlib
from functools import wraps
import os

from filelock import FileLock

from litkit import utils, cache as ca
import pandas as pd

pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def cache(ignore=[]):
    def deco(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            max_age = utils.get_arg(fn, args, kwargs, "max_age")
            if max_age == 0:
                return fn(*args, **kwargs)

            key = utils.serialize_call(fn, args, kwargs, ignore)
            if len(key) > 200:
                key = hashlib.sha256(str(key).encode('utf-8')).hexdigest()

            lock_dir = '/tmp/lock/'
            if not os.path.exists(lock_dir):
                os.makedirs(lock_dir)

            lock = FileLock(lock_dir + key)

            with lock:
                use_cache = ca.get(key, max_age)

                if use_cache is True:
                    df = ca.__read_df(key)
                    if df is not None:
                        return df

                df = fn(*args, **kwargs)

                ca.__write_df(df, key)
                ca.set(key, True)

                return df

        return wrapper

    return deco