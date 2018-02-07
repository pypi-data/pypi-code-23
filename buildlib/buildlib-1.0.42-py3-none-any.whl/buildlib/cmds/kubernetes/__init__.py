from typing import List, Union
import sys
import subprocess as sp
from cmdinter import CmdFuncResult, Status
from functools import reduce


def _parse_option(
    args: Union[bool, list, str],
    flag: str,
) -> list:
    """"""
    if type(args) == list:
        nested = [[flag, f] for f in args]
        return reduce(lambda x, y: x + y, nested)
    elif type(args) == str:
        return [flag, args]
    elif type(args) == bool:
        return [flag] if args is True else []
    else:
        return []


def apply(
    stdin: str = None,
    files: List[str] = None,
    namespace: List[str] = 'default',
) -> CmdFuncResult:
    """
    @std: Use this to pass a config string via stdin.
    """
    title = 'kubectl apply.'

    if stdin and files:
        sys.stderr('Cannot use parameter "stdin" and "files" at the same time')
        sys.exit(1)

    options = [
        *_parse_option(namespace, '--namespace'),
        *_parse_option(files, '-f'),
    ]

    cmd = ['kubectl', 'apply'] + options

    if stdin:
        cmd += ['-f', '-']

    p = sp.Popen(cmd, stdin=sp.PIPE)

    if stdin:
        p.stdin.write(stdin.encode())

    p.communicate()

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )
