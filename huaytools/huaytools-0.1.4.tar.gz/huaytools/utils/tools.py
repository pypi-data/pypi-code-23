import time
import functools


def timing(func):
    """函数计时装饰器

    Args:
        func: 被装饰的函数

    Examples:

        >>> @timing
        ... def t(seconds=2):
        ...     time.sleep(seconds)
        ...
        >>> _, duration = t()

    Returns:
        (Any, float): 原函数的返回值，以及所用时间

    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        return ret, time.time() - start

    return inner

