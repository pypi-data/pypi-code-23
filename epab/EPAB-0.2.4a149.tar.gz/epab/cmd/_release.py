# coding=utf-8
"""
Creates a wheel from a Github repo
"""
import os
import shutil
import sys

import click

import epab.cmd._reqs
import epab.linters
import epab.utils
from epab.core import CONFIG, CTX, VERSION

from ._chglog import chglog
from ._pytest import pytest


def _clean():
    """
    Cleans up build dir
    """
    epab.utils.info(f'Cleaning project directory...')
    if CTX.dry_run:
        return
    folders_to_cleanup = [
        '.eggs',
        'build',
        f'{CONFIG.package}.egg-info',
    ]
    for folder in folders_to_cleanup:
        if os.path.exists(folder):
            epab.utils.info(f'\tremoving: {folder}')
            shutil.rmtree(folder)


def _release(ctx):
    current_branch = CTX.repo.get_current_branch()
    next_version = epab.utils.get_git_version_info()
    epab.utils.info(f'Current version -> {VERSION}')
    epab.utils.info(f'Current branch  -> {current_branch}')
    epab.utils.info(f'Next version    -> {next_version}')

    epab.utils.info('Checking repo')
    if CTX.repo.is_dirty(untracked=True):
        epab.utils.error('Repository is dirty, cannot release')
        exit(1)

    if CTX.dry_run:
        epab.utils.info('Skipping release; DRY RUN')
        return

    CTX.stash = False
    ctx.invoke(epab.linters.lint)
    if CTX.repo.is_dirty(untracked=True):
        epab.utils.error('Linters produced artifacts, aborting release')
        exit(1)

    ctx.invoke(pytest, long=True)

    ctx.invoke(epab.cmd.reqs, amend=True)

    CTX.repo.tag(next_version)
    ctx.invoke(chglog, amend=True)
    CTX.repo.remove_tag(next_version)

    CTX.repo.amend_commit(f'release {next_version}')
    CTX.repo.tag(next_version)

    _clean()

    python_exe = sys.executable.replace('\\', '/')
    epab.utils.run(f'{python_exe} setup.py sdist bdist_wheel')
    epab.utils.run(f'twine upload dist/* --skip-existing --repository-url https://test.pypi.org/legacy/', mute=True)
    exit(0)
    CTX.repo.push()

    # exit(0)
    #
    # if 'develop' not in [current_branch, os.getenv('APPVEYOR_REPO_BRANCH')]:
    #     epab.utils.error(f'Not on develop; skipping release (current branch: {current_branch})')
    #     exit(0)
    #
    # if current_branch == 'HEAD' and os.getenv('APPVEYOR_REPO_BRANCH') == 'develop':
    #     CTX.repo.checkout('develop')
    #
    # epab.utils.info('Making new release')
    #
    # ctx.invoke(pytest, long=True)
    #
    # ctx.invoke(epab.linters.lint)
    #
    # # FIXME
    # # new_version = epab.utils.bump_version(ctx, new_version)
    # epab.utils.info(f'New version: {new_version}')
    # CTX.repo.tag(new_version)
    # ctx.invoke(chglog)
    # CTX.repo.remove_tag(new_version)
    #
    # CTX.repo.amend_commit(f'release {new_version}')
    # CTX.repo.checkout('master')
    # CTX.repo.merge('develop')
    # CTX.repo.tag(new_version)
    #
    # try:
    #
    #     _clean()
    #
    #     if CTX.dry_run:
    #         epab.utils.info('DRYRUN: All good!')
    #         return
    #     python_exe = sys.executable.replace('\\', '/')
    #     epab.utils.run(f'{python_exe} setup.py bdist_wheel')
    #     epab.utils.run(f'twine upload dist/* --skip-existing', mute=True)
    #
    #     CTX.repo.checkout('develop')
    #     CTX.repo.push()
    #
    #     if CONFIG.package != 'epab':
    #         epab.utils.run('pip install -e .')
    #     epab.utils.info('All good!')
    #
    # except SystemExit:
    #     CTX.repo.checkout('develop')
    #     _clean()
    #     CTX.repo.remove_tag(new_version)
    #
    #     if CONFIG.package != 'epab':
    #         epab.utils.run('pip install -e .')
    #     raise


@click.command()
@click.pass_context
def release(ctx):
    """
    This is meant to be used as a Git pre-push hook
    """
    _release(ctx)
