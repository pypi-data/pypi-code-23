# coding=utf-8
"""
Manages the release process on Appveyor
"""

import os

import click

import epab.linters
import epab.utils
from epab import __version__
from epab.core import CTX

from ._pytest import pytest
from ._release import release


def _appveyor_branch():  # pragma: no cover
    return os.getenv('APPVEYOR_REPO_BRANCH')


def _appveyor_commit():  # pragma: no cover
    return os.getenv('APPVEYOR_REPO_COMMIT')


def _appveyor_build():  # pragma: no cover
    return os.getenv('APPVEYOR_BUILD_NUMBER')


def _appveyor_update_build(version: str):  # pragma: no cover
    epab.utils.run(f'appveyor UpdateBuild -Version {version}-{_appveyor_build()}-{_appveyor_commit()}')


@epab.utils.run_once
def _appveyor(ctx):
    epab.utils.info('RUNNING APPVEYOR RELEASE')
    epab.utils.info(f'Current version: {__version__}')
    epab.utils.info(f'Latest tag: {CTX.repo.get_latest_tag()}')
    _appveyor_update_build(CTX.repo.get_latest_tag())

    epab.utils.info('Running tests')
    ctx.invoke(pytest)

    epab.utils.info('Uploading coverage info')
    epab.utils.run('pip install --upgrade codacy-coverage')
    epab.utils.run('python-codacy-coverage -r coverage.xml')

    # Covered by AV
    # if not ctx.obj['CONFIG']['package'] == 'epab':
    #     info('Installing current package with pipenv')
    #     do(ctx, ['pipenv', 'install', '.'])

    if os.path.exists('appveyor.yml'):
        epab.utils.info('Removing leftover "appveyor.yml" file')
        os.unlink('appveyor.yml')

    commit_msg = os.getenv('APPVEYOR_REPO_COMMIT_MESSAGE_EXTENDED')
    if commit_msg:
        if 'release ' in commit_msg.lower():
            tag = commit_msg.lower().replace('release ', '')
            epab.utils.info(f'using tag from commit message: {tag}')
            CTX.next_version = tag

    if os.getenv('APPVEYOR_REPO_BRANCH') == 'develop':
        epab.utils.info('We\'re on develop; making new release')
        ctx.invoke(release)
    else:
        epab.utils.info('Not on develop, skipping release')
        ctx.invoke(epab.linters.lint, auto_commit=False)

    _appveyor_update_build(CTX.repo.get_latest_tag())
    epab.utils.info('ALL DONE')


@click.command()
@click.pass_context
def appveyor(ctx: click.Context):
    """
    Manages the release process on Appveyor
    """
    _appveyor(ctx)
