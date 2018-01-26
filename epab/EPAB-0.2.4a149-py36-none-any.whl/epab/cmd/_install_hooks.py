# coding=utf-8
"""
Installs Git hooks
"""
from pathlib import Path

import click

import epab.utils
from epab.core import VERSION


PRE_PUSH = """#!/bin/sh
#
# This Git hook was installed by EPAB {version}
#
PATH="{venv}:$PATH"
echo `epab --version`

epab -d reqs chglog

epab -d lint
if [ "$?" -ne "0" ]
then
    echo "Linting failed"
    exit 1
fi

git diff-index --quiet --cached HEAD --
if [ "$?" -ne "0" ]
then
    echo "There are uncommitted staged changes"
    exit 1
fi

git diff-files --quiet
if [ "$?" -ne "0" ]
then
    echo "There are untracked files"
    exit 1
fi
exit 0"""


def _make_venv_path() -> str:
    venv, _ = epab.utils.run('pipenv --venv')
    venv = Path(venv, 'Scripts').absolute()
    return Path('/', venv.parts[0].replace(':', '').lower(), *venv.parts[1:]).as_posix()


def _install_hooks():
    Path('./.git/hooks/pre-push').write_text(
        PRE_PUSH.format(venv=_make_venv_path(), version=VERSION)
    )


@click.command()
def install_hooks():
    """
    Install Git hooks

    Args:
        ctx: click Context

    """
    _install_hooks()
