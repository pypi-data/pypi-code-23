# coding=utf-8
"""
Utilities to control the console window
"""

import ctypes
import logging

import click

from elib.settings import ELIBSettings

LOGGER = logging.getLogger('ELIB')


def set_title(title: str):  # pragma: no cover
    """
    Sets the console title

    Args:
        title: title as a string
    """
    LOGGER.debug(f'setting console title to {title}')
    ctypes.windll.kernel32.SetConsoleTitleW(title)


def _sanitize(input_: str, prefix=True) -> str:
    if prefix:
        input_ = f'EPAB: {input_}'
    return input_.encode('ascii', 'ignore').decode()


def _output(txt, color, **kwargs) -> str:
    if not ELIBSettings.quiet:
        click.secho(txt, fg=color, **kwargs)
    return txt


def info(txt: str, **kwargs):
    """
    Prints out informative text

    :param txt: text to print
    :param kwargs: additional arguments to `click.secho` command
    """
    txt = _sanitize(txt)
    _output(txt, ELIBSettings.color_info, **kwargs)


def error(txt: str, **kwargs):
    """
    Prints out an error

    :param txt: text to print
    :param kwargs: additional arguments to `click.secho` command
    """
    txt = _sanitize(txt)
    _output(txt, ELIBSettings.color_error, err=True, **kwargs)


def cmd_start(txt: str, **kwargs):
    """
    Prints out the start of a sub-process

    This command should be followed by à call to `cmd_end`

    :param txt: text to print
    :param kwargs: additional arguments to `click.secho` command
    """
    txt = _sanitize(txt)
    _output(txt, ELIBSettings.color_cmd, nl=False, **kwargs)


def cmd_end(txt: str, **kwargs):
    """
    Prints out the end of a sub-process

    This should follow a call to `cmd_start`

    :param txt: text to print
    :param kwargs: additional arguments to `click.secho` command
    """
    txt = _sanitize(txt, prefix=False)
    _output(txt, ELIBSettings.color_cmd, **kwargs)


def std_out(txt: str, **kwargs):
    """
    Prints out text from a sub-process standard out stream

    :param txt: text to print
    :param kwargs: additional arguments to `click.secho` command
    """
    txt = _sanitize(f'{txt}', prefix=False)
    _output(txt, ELIBSettings.color_stdout, nl=False, **kwargs)


def std_err(txt: str, **kwargs):
    """
    Prints out text from a sub-process standard error stream

    :param txt: text to print
    :param kwargs: additional arguments to `click.secho` command
    """
    txt = _sanitize(txt, prefix=False)
    _output(txt, ELIBSettings.color_stderr, err=True, **kwargs)
