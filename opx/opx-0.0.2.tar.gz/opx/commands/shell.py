import logging

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command(help='Launch an OPX development shell.')
@click.option('--dist', default='unstable',
              help='OPX distribution to build against.')
@click.option('--remove-container', is_flag=True,
              help='Remove container when command exits.')
@config.pass_config
def shell(c: config.Config, dist: str, remove_container: bool) -> None:
    run.in_container(c=c, dist=dist, remove=remove_container)