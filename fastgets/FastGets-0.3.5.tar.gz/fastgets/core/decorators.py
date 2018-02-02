from functools import wraps


def sync(lock):
    def catch_func(func):
        @wraps(func)
        def catch_args(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return catch_args
    return catch_func
