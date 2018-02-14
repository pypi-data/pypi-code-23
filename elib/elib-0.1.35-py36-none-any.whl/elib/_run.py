# coding=utf-8
"""
Manages runners
"""

import os
import sys
import typing
from pathlib import Path

import click
import delegator

from elib.console import cmd_end, cmd_start, error, info, std_err, std_out
from elib.settings import ELIBSettings

KNOWN_EXECUTABLES = {}


def _append_exe(executable):
    if not executable.endswith('.exe'):
        return f'{executable}.exe'

    return executable


def _set_paths(*paths: str):
    if not paths:
        path = os.environ['PATH']
        paths = [Path(sys.exec_prefix, 'Scripts').absolute()] + path.split(os.pathsep)

    return paths


def _search_paths(paths, executable):
    for path_ in paths:
        executable_path = Path(path_, executable).absolute()
        if executable_path.is_file():
            break
    else:
        cmd_end(f' -> not found')
        return None

    return executable_path


def find_executable(executable: str, *paths: str) -> typing.Optional[Path]:  # noqa: C901
    # noinspection SpellCheckingInspection
    """
    https://gist.github.com/4368898

    Public domain code by anatoly techtonik <techtonik@gmail.com>

    Programmatic equivalent to Linux `which` and Windows `where`

    Find if ´executable´ can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.

    Args:
        executable: executable name to look for
        paths: root paths to examine (defaults to system PATH)

    Returns: executable path as string or None

    """

    executable = _append_exe(executable)

    if executable in ELIBSettings.known_executables:  # type: ignore
        return ELIBSettings.known_executables[executable]  # type: ignore

    cmd_start(f'Looking for executable: {executable}')

    paths = _set_paths(*paths)

    executable_path = Path(executable)
    if not executable_path.is_file():
        executable_path = _search_paths(paths, executable)

    if executable_path is None:
        cmd_end(f' -> not found')
        return None

    ELIBSettings.known_executables[executable] = executable_path
    cmd_end(f' -> {click.format_filename(str(executable_path))}')
    return executable_path


def filter_line(
        line: str,
        filters: typing.Optional[typing.Iterable[str]]
) -> typing.Optional[str]:
    """
    Filters out line that contain substring

    Args:
        line: line to filter
        filters: filter strings to apply

    Returns: line if not filter are found in line, else None

    """
    if filters is not None:
        for filter_ in filters:
            if filter_ in line:
                return None
    return line


def _parse_output(process, filters):
    result = []
    for line in process.out.splitlines():
        if filter_line(line, filters):
            result.append(line)
    for line in process.err.splitlines():  # pragma: no cover
        if filter_line(line, filters):
            result.append(line)

    return '\n'.join(result)


def _process_run_error(
        mute,
        result,
        failure_ok,
        process,
        exe_short
):
    if mute:
        cmd_end('')
    error(f'command failed: {exe_short} -> {process.return_code}')
    if result:
        std_err(f'{exe_short} error:\n{result}')
        if not result.endswith('\n'):  # pragma: no cover
            print()
    if not failure_ok:
        exit(process.return_code)


def _process_run_success(
        mute,
        result,
        process,
        exe_short
):
    if mute:
        cmd_end(f' -> {process.return_code}')
    else:
        std_out(result)
        if not result.endswith('\n'):  # pragma: no cover
            print()
        info(f'{exe_short} -> {process.return_code}')


def _process_run_result(process, mute, exe_short, failure_ok, result) -> typing.Tuple[str, int]:
    if process.return_code:
        _process_run_error(
            mute=mute,
            result=result,
            failure_ok=failure_ok,
            process=process,
            exe_short=exe_short,
        )
    else:
        _process_run_success(
            mute=mute,
            result=result,
            process=process,
            exe_short=exe_short,
        )

    return result, process.return_code


def _prepare_run_setup_filters(filters):
    if filters and isinstance(filters, str):
        filters = [filters]

    return filters


def _prepare_run_find_exe(cmd, *paths):
    exe = find_executable(cmd.split(' ')[0], *paths)
    if not exe:
        exit(-1)
    return exe


def _prepare_run_advertise(mute, cmd):
    mute = mute and not ELIBSettings.verbose

    if mute:
        cmd_start(f'RUNNING: {cmd}')
    else:
        info(f'RUNNING: {cmd}')


def run(
        cmd: str,
        *paths: str,
        cwd: str = '.',
        mute: bool = False,
        filters: typing.Union[None, typing.Iterable[str]] = None,
        failure_ok: bool = False,
) -> typing.Tuple[str, int]:
    """
    Executes a command and returns the result

    Args:
        cmd: command to execute
        paths: paths to search executable in
        cwd: working directory (defaults to ".")
        mute: if true, output will not be printed
        filters: gives a list of partial strings to filter out from the output (stdout or stderr)
        failure_ok: if False (default), a return code different than 0 will exit the application

    Returns: command output
    """

    filters = _prepare_run_setup_filters(filters)

    exe = _prepare_run_find_exe(cmd, *paths)
    exe_short = exe.name

    cmd = ' '.join([f'"{exe.absolute()}"'] + cmd.split(' ')[1:])

    _prepare_run_advertise(mute, cmd)

    process = delegator.run(cmd, block=True, cwd=cwd, binary=False)
    result = _parse_output(process, filters)

    return _process_run_result(process, mute, exe_short, failure_ok, result)
