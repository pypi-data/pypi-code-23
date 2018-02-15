import logging

from pathlib import Path
from typing import Tuple

import click

from opx import config
from opx import gbp

L = logging.getLogger(config.APP_NAME)


@click.command()
@click.option('--dist',
              help='Change OPX distribution to build against.')
@click.option('--rm', is_flag=True,
              help='Remove container when command exits.')
@click.option('--sort', is_flag=True,
              help='Move artifacts from workspace to workspace/pkg/repo/.')
@click.argument('repos', nargs=-1)
@config.pass_config
def build(c: config.Config, dist: str, rm: bool, sort: bool, repos: Tuple[str]) -> None:
    """Build one or more OpenSwitch repositories.

    REPOS are built using git-buildpackage inside a container.

    OpenSwitch build dependencies are pulled from the DIST distribution if not present locally.
    """
    if len(repos) == 0:
        # trailing comma creates single item tuple
        if Path().cwd() == c.root:
            repos = 'all',
        else:
            repos = str(Path().cwd().name),

    dist = c.get_dist(dist)

    for repo in repos:
        gbp.buildpackage(c, repo, dist, rm, sort, tag=False)
