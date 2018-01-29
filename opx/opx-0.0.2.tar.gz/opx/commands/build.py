import logging

from pathlib import Path
from typing import Tuple

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command(help='Build one or more repositories.')
@click.option('--dist', default='unstable',
              help='OPX distribution to build against.')
@click.option('--remove-container', is_flag=True,
              help='Remove container when command exits.')
@click.argument('repos', nargs=-1)
@config.pass_config
def build(c: config.Config, dist: str, remove_container: bool, repos: Tuple[str]) -> None:
    if len(repos) == 0:
        # trailing comma creates single item tuple
        if Path().cwd() == c.root:
            repos = "all",
        else:
            repos = str(Path().cwd().name),
    for repo in repos:
        run.in_container(c=c, dist=dist, remove=remove_container, cmd=f'opx_build {repo}')