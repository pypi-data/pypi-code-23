from threading import currentThread


LOCAL_CACHE = {}


class local_cache(object):
    """
    A decorator or context manager that will cache some values for the
    lifetime of the decorator/context manager.
    """
    def _function(self, func, *args, **kwargs):
        def wrapped(*args, **kwargs):
            try:
                self.__enter__()
                value = func(*args, **kwargs)
            finally:
                self.__exit__()
            return value
        return wrapped

    # This handles function decorators + class decorators.  Needs to switch
    # on argument type :(
    def __call__(self, decorated, *args, **kwargs):
        if isinstance(decorated, type):
            raise Exception("Can only decorate a function, not a class")

        return self._function(decorated, *args, **kwargs)

    # These handle context managers, and are used by the others
    def __enter__(self, *args, **kwargs):
        thread = currentThread()

        LOCAL_CACHE[thread] = {}
        return self

    def __exit__(*args, **kwargs):
        thread = currentThread()
        del LOCAL_CACHE[thread]


def _get_local_cache():
    thread = currentThread()
    if thread in LOCAL_CACHE:
        return LOCAL_CACHE[thread]
    if hasattr(thread, 'parent'):
        thread = thread.parent
        if thread in LOCAL_CACHE:
            return LOCAL_CACHE[thread]

    return


def set_cache_value(key, value):
    """
    If local cache is being used, this will set a cache value for the
    lifetime of that cache.
    """
    cache = _get_local_cache()
    if cache is None:
        return

    cache[key] = value


def get_cache_value(key):
    """
    If local cache is being used, this will get the cache value, if it exists.
    """
    cache = _get_local_cache()
    if cache is None:
        return

    if key in cache:
        return cache[key]
