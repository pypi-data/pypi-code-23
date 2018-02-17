"""工具函数（如果不知道应该归到哪个模块文件，就放在这里）
"""
from typing import Iterable


def yield_cycling(iterator):
    """无限循环迭代器

    itertools 提供了类似的方法
        from itertools import cycle
    但是该方法（好像）需要复制

    Args:
        iterator (Iterable): 可迭代对象

    Examples:

        >>> it = yield_cycling([1, 2, 3])
        >>> for _ in range(4):
        ...     print(next(it))
        1
        2
        3
        1

    """
    while True:
        yield from iter(iterator)


