import logging

from pathlib import Path
from typing import Tuple

import click

from opx import config
from opx import run
from opx.exceptions import CliException

L = logging.getLogger(config.APP_NAME)


@click.command()
@click.option('--dist', default='unstable',
              help='OPX distribution to build against.')
@click.option('--url', '-u', default=config.OPX_MANIFEST,
              help='Manifest repository URL')
@click.option('--manifest', '-m', default='default.xml',
              help='Manifest file within repository')
@click.option('--branch', '-b', default='master',
              help='Branch of repository to use')
@click.argument('projects', nargs=-1,)
@config.pass_config
def init(c: config.Config, dist: str, url: str, manifest: str, branch: str, projects: Tuple[str]):
    """Initialize an OpenSwitch workspace.

    Runs repo init and repo sync. DIST will be saved in workspace configuration.

    URL, MANIFEST, BRANCH, and PROJECTS are passed directly to repo.

    Examples:

    opx init

        Create a workspace with the latest content from each repository.

    opx init --dist stable

        Create a workspace with the latest stable packages.

    opx init --dist 2.2.1

        Create a workspace for the 2.2.1 release.

    opx init --release 2.2 (coming soon)

        Create a workspace with each repository's HEAD pointing to the tag of
        the package in the release. When building, missing dependencies are
        pulled from the exact set of packages used to build the release
        initially. A release can be recreated from code by running:

            opx build all && opx assemble --dist 2.2 -n 0
    """
    if c.root is not None:
        raise CliException('This directory is already inside a workspace.')

    c.new(Path().cwd(), dist)
    cmd = 'repo init -u {} -m {} -b {}'.format(url, manifest, branch)
    run.noninteractive(cmd, 'Initializing repositories...')
    cmd = 'repo sync {projects}'.format(projects=' '.join(projects))
    run.noninteractive(cmd, 'Synchronizing repositories...')
    c.write()
