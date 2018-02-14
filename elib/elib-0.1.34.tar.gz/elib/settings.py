# coding=utf-8
"""
ELIB settings
"""


class ELIBSettings:
    """
    ELIB settings
    """

    mute: bool = False
    quiet: bool = False
    verbose: bool = False
    known_executables: dict = {}

    color_info = 'green'
    color_error = 'red'
    color_cmd = 'magenta'
    color_stdout = 'cyan'
    color_stderr = 'red'
