import logging

import click

from opx import config
from opx import gbp

L = logging.getLogger(config.APP_NAME)


@click.command()
@click.option('--rm', is_flag=True,
              help='Remove container when command exits.')
@click.option('--stable', is_flag=True,
              help='Prepare for promotion to stable.')
@click.argument('repo')
@config.pass_config
def release(c: config.Config, stable: bool, rm: bool,  repo: str) -> None:
    """Tag an OpenSwitch repository.

    The REPO is built using git-buildpackage inside a container.
    Build dependencies are pulled from the testing distribution of OPX if not present locally.
    Results are found in pkg/REPO.
    """
    dist = 'stable' if stable else 'testing'
    gbp.buildpackage(c, repo, dist, rm, sort=True, tag=True)
