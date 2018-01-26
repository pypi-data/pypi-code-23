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

from ._release import release


def _appveyor_branch():
    return os.getenv('APPVEYOR_REPO_BRANCH')


def _appveyor_commit():
    return os.getenv('APPVEYOR_REPO_COMMIT')


def _appveyor_build():
    return os.getenv('APPVEYOR_BUILD_NUMBER')


def _appveyor_update_build(version: str):
    epab.utils.run(f'appveyor UpdateBuild -Version {version}-{_appveyor_build()}-{_appveyor_commit()}')


@epab.utils.run_once
def _appveyor(ctx):
    epab.utils.info('RUNNING APPVEYOR RELEASE')
    epab.utils.info(f'Current version: {__version__}')
    epab.utils.info(f'Latest tag: {CTX.repo.get_latest_tag()}')

    next_version = epab.utils.get_git_version_info()
    epab.utils.info(f'Building next version: {next_version}')
    _appveyor_update_build(next_version)

    # CTX.repo.checkout(_appveyor_branch())

    if os.path.exists('appveyor.yml'):
        epab.utils.info('Removing leftover "appveyor.yml" file')
        os.unlink('appveyor.yml')

    epab.utils.info(f'Running on commit: {CTX.repo.latest_commit()}')

    ctx.invoke(release)

    epab.utils.info('Uploading coverage info')
    epab.utils.run('pip install --upgrade codacy-coverage')
    epab.utils.run('python-codacy-coverage -r coverage.xml')


@click.command()
@click.pass_context
def appveyor(ctx: click.Context):
    """
    Manages the release process on Appveyor
    """
    _appveyor(ctx)
