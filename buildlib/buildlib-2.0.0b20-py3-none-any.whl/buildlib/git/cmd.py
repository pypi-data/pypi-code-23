import subprocess as sp
from typing import Optional
from cmdi import command, CmdResult, CustomCmdResult


@command
def add_all() -> CmdResult:
    """"""
    sp.run(
        ['git', 'add', '--all'],
        check=True,
    )


@command
def commit(
    msg: str
) -> CmdResult:
    """"""
    sp.run(
        ['git', 'commit', '-m', msg],
        check=True,
    )


@command
def tag(
    version: str,
    branch: str,
) -> CmdResult:
    """"""
    sp.run(
        ['git', 'tag', version, branch],
        check=True,
    )


@command
def push(branch: str) -> CmdResult:
    """"""
    sp.run(
        ['git', 'push', 'origin', branch, '--tags'],
        check=True,
    )


@command
def get_default_branch() -> CmdResult:
    """"""
    branch: Optional[str] = None

    p1 = sp.run(
        ['git', 'show-branch', '--list'],
        stdout=sp.PIPE,
        check=True,
    )

    if p1.stdout.decode().find('No revs') == -1 and p1.returncode == 0:
        p2 = sp.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=sp.PIPE,
            check=True,
        )

        branch: str = p2.stdout.decode().replace('\n', '')

    return branch


@command
def status() -> CmdResult:
    """"""
    sp.run(
        ['git', 'status'],
        check=True,
    )


@command
def diff() -> CmdResult:
    """"""
    sp.run(
        ['git', 'diff'],
        check=True,
    )
