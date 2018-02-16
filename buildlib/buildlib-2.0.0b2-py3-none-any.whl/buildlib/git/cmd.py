from processy import run, CompletedProcess
from typing import Optional
from cmdi import command, CmdResult, CustomCmdResult


@command
def add_all() -> CmdResult:
    """"""
    p: CompletedProcess = run(cmd=['git', 'add', '--all'])


@command
def commit(
    msg: str
) -> CmdResult:
    """"""
    p: CompletedProcess = run(cmd=['git', 'commit', '-m', msg])


@command
def tag(
    version: str,
    branch: str,
) -> CmdResult:
    """"""
    p: CompletedProcess = run(cmd=['git', 'tag', version, branch])


@command
def push(branch: str) -> CmdResult:
    """"""
    p: CompletedProcess = run(cmd=['git', 'push', 'origin', branch, '--tags'])


@command
def get_default_branch() -> CmdResult:
    """"""
    branch: Optional[str] = None

    p1 = run(
        cmd=['git', 'show-branch', '--list'],
        return_stdout=True
    )

    if p1.stdout.find('No revs') == -1 and p1.returncode == 0:
        p2 = run(
            cmd=['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            return_stdout=True
        )

        branch: str = p2.stdout.replace('\n', '')

    return branch


@command
def status() -> CmdResult:
    """"""
    p: CompletedProcess = run(cmd=['git', 'status'])


@command
def diff() -> CmdResult:
    """"""
    p: CompletedProcess = run(cmd=['git', 'diff'])
