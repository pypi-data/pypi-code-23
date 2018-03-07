"""工具函数（如果不知道应该归到哪个模块文件，就放在这里）
"""
import os
import sys
import platform
from typing import Iterable

import logging

def yield_cycling(iterator):
    """
    无限循环迭代器

    itertools 提供了类似的方法
        from itertools import cycle

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


def system_is(system_type):
    """
    判断系统类型

    Args:
        system_type(str): 系统类型，可选 "linux", "windows", ..

    Returns:
        bool

    Examples:
        >>> if system_is("windows"):
        ...     print("Windows")
        Windows

    """
    if system_type in ['win', 'Win', 'windows', 'Windows', 'window', 'Window']:
        system_type = 'Windows'
    else:
        system_type = 'Linux'
    return system_type == platform.system()


def get_logger(name=None, fname=None, mode='a', level=logging.INFO, stream=None,
               fmt="[%(name)s] : %(asctime)s : %(levelname)s : %(message)s"):
    """
    默认输出到终端，如果提供了 log_fname，则同时输出到文件和终端

    Returns:
        logger

    Examples:
        >>> logger = get_logger(stream=sys.stdout, fmt="[%(name)s] : %(levelname)s : %(message)s")
        >>> logger.info("test")
        [tools.py] : INFO : test


    """
    if name is None:
        # name = os.path.splitext(os.path.basename(__file__))[0]
        name = os.path.basename(__file__)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    fmt = logging.Formatter(fmt)

    ch = logging.StreamHandler(stream)
    ch.setFormatter(fmt)

    logger.addHandler(ch)

    if fname is not None:
        fh = logging.FileHandler(fname, mode)
        fh.setFormatter(fmt)

        logger.addHandler(fh)

    return logger
