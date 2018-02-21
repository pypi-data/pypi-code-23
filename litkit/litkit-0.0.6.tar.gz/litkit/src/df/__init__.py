import hashlib
from functools import wraps
import os

from beeprint import pp
from filelock import FileLock
from pandas.core.dtypes.common import is_numeric_dtype

from litkit.src import utils, cache as ca
import pandas as pd
import numpy as np

from litkit.src.df import vis


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


def info(df: pd.DataFrame):
    stats = {
        'column': [],
        'type': [],
        'unique_n': [],
        'unique_samples': [],
        'nan_n': [],
        'non_nan_n': [],
        'length': [],
        'kB': [],
        'kB_deep': [],
        'mean': [],
        'std': [],
        'min': [],
        '25%th': [],
        '50%th': [],
        '75%th': [],
        '90%th': [],
        '99%th': [],
        'max': [],
    }

    for c in df.columns:
        s = df[c]
        stats['column'].append(c)
        stats['type'].append(s.dtype)
        u = s.unique()
        stats['unique_n'].append(len(u))

        if len(u) > 5:
            u = np.array(u[:5])
            try:
                if u.dtype == 'object':
                    u = u.astype('float')
            except:
                pass

            if np.issubdtype(u.dtype, np.number):
                u = np.around(u, 2)

        stats['unique_samples'].append(u)

        nan_c = s.isnull().sum()
        length = len(s)

        stats['nan_n'].append(nan_c)
        stats['non_nan_n'].append(length - nan_c)
        stats['length'].append(length)
        stats['kB'].append(round(s.memory_usage() / 1024, 1))
        stats['kB_deep'].append(round(s.memory_usage(deep=True) / 1024, 1))

        v = s.dropna().values
        try:
            if v.dtype == 'object':
                v = v.astype('float')
        except:
            stats['mean'].append(None)
            stats['std'].append(None)
            stats['min'].append(None)
            stats['25%th'].append(None)
            stats['50%th'].append(None)
            stats['75%th'].append(None)
            stats['90%th'].append(None)
            stats['99%th'].append(None)
            stats['max'].append(None)
            continue

        stats['mean'].append(round(np.mean(v), 1))
        stats['std'].append(round(np.std(v), 1))
        stats['min'].append(round(np.min(v), 1))
        stats['25%th'].append(round(np.percentile(v, 25), 2))
        stats['50%th'].append(round(np.percentile(v, 50), 2))
        stats['75%th'].append(round(np.percentile(v, 75), 2))
        stats['90%th'].append(round(np.percentile(v, 90), 2))
        stats['99%th'].append(round(np.percentile(v, 99), 2))
        stats['max'].append(round(np.max(v), 1))

    stats_df = pd.DataFrame(stats)

    stats_df = stats_df[['column', 'type', 'length', 'kB', 'kB_deep', 'nan_n', 'non_nan_n', 'unique_n', 'unique_samples', 'mean', 'std', 'min', '25%th', '50%th', '75%th', '90%th', '99%th', 'max']]

    print('\n\nmemory: {}kB deep: {}kB'.format(round(df.memory_usage().sum() / 1024, 1), round(df.memory_usage(deep=True).sum() / 1024, 1)))

    print('\ncolumn types:')

    pp(stats_df['type'].value_counts().sort_index())

    print()

    pp(stats_df)
