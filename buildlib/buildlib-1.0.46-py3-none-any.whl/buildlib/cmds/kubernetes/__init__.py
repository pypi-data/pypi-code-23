from typing import List, Union
import sys
from processy import run
import subprocess as sp
from cmdinter import CmdFuncResult, Status
from functools import reduce


def _parse_option(
    flag: str,
    args: List[str],
) -> list:
    """"""
    if type(args) == list:
        return [flag, ','.join(args)]
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
        *_parse_option('-n', namespace),
        *_parse_option('-f', files),
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

    # if delete:
    #     cmd = ['kubectl', 'delete', 'pods,replicaSets', '-l', label, '-n',
    #            s.NAMESPACE, '--now']
    #     p = sp.run(cmd)


def delete(
    type_: List[str],
    label: List[str] = None,
    namespace: List[str] = 'default',
) -> CmdFuncResult:
    """
    @type_: pods, replicaSets, deployments, etc'
    """
    title = 'kubectl delete.'

    options = [
        *_parse_option('-l', label),
        *_parse_option('-n', namespace),
    ]

    cmd = ['kubectl', 'delete', ','.join(type_)] + options

    p = run(cmd, stdin=sp.PIPE)

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )
