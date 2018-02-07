from contextlib import contextmanager
from tempfile import NamedTemporaryFile


def yaml_dump_omaps(s):
    from ruamel import yaml
    res = yaml.dump(s, Dumper=yaml.RoundTripDumper, allow_unicode=False)
    return res


def yaml_load_omaps(s):
    from ruamel import yaml
    res = yaml.load(s, Loader=yaml.UnsafeLoader)
    return res


@contextmanager
def tmpfile(suffix):
    ''' Yields the name of a temporary file '''
    temp_file = NamedTemporaryFile(suffix=suffix)
    try:
        yield temp_file.name
    finally:
        temp_file.close()

# -*- coding: utf-8 -*-


from decorator import decorator

__all__ = [
    'memoize_simple',
]


def memoize_simple(obj):
    cache = obj.cache = {}

    def memoizer(f, *args):
        key = (args)
        if key not in cache:
            cache[key] = f(*args)
        assert key in cache

        try:
            cached = cache[key]
            return cached
        except ImportError:  # pragma: no cover  # impossible to test
            del cache[key]
            cache[key] = f(*args)
            return cache[key]

            # print('memoize: %s %d storage' % (obj, len(cache)))

    return decorator(memoizer, obj)
