# coding=utf-8
"""
Utilities to control the console window
"""

import ctypes
import logging

LOGGER = logging.getLogger('ELIB')


def set_title(title: str):  # pragma: no cover
    """
    Sets the console title

    Args:
        title: title as a string
    """
    LOGGER.debug(f'setting console title to {title}')
    ctypes.windll.kernel32.SetConsoleTitleW(title)
