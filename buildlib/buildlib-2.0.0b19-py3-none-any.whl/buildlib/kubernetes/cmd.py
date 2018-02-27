from typing import List, Union
import sys
import subprocess as sp
from cmdi import command, CmdResult, CustomCmdResult


def _parse_option(
    flag: str,
    args: List[str],
) -> list:
    """"""
    if type(args) == list:
        return [flag, ','.join(args)]
    else:
        return []


@command
def apply(
    stdin: str = None,
    files: List[str] = None,
    namespace: List[str] = 'default',
    **cmdargs,
) -> CmdResult:
    """
    @std: Use this to pass a config string via stdin.
    """
    if stdin and files:
        sys.stderr('Cannot use parameter "stdin" and "files" at the same time')
        sys.exit(1)

    options = [
        *_parse_option('-n', namespace),
        *_parse_option('-f', files),
    ]

    cmd = ['kubectl', 'apply'] + options

    if stdin:
        cmd += ['-f', '-']

    p = sp.Popen(cmd, stdin=sp.PIPE)

    if stdin:
        p.stdin.write(stdin.encode())

    output, error = p.communicate()

    if p.returncode != 0:
        raise sp.CalledProcessError(p.returncode, cmd)


@command
def delete(
    type_: List[str],
    label: List[str] = None,
    namespace: List[str] = 'default',
    **cmdargs,
) -> CmdResult:
    """
    @type_: pods, replicaSets, deployments, etc'
    """
    options = [
        *_parse_option('-l', label),
        *_parse_option('-n', namespace),
    ]

    sp.run(
        ['kubectl', 'delete', ','.join(type_)] + options,
        check=True,
    )
