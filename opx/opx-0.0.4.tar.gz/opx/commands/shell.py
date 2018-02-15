import logging

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command()
@click.option('--dist',
              help='Change OPX distribution to build against.')
@click.option('--rm', is_flag=True,
              help='Remove container when command exits.')
@config.pass_config
def shell(c: config.Config, dist: str, rm: bool) -> None:
    """Launch an OpenSwitch development container.

    Creates a build container and runs bash inside.

    Build dependencies are pulled from the DIST distribution of OPX if not present locally.
    """
    dist = c.get_dist(dist)

    run.in_container(c=c, dist=dist, remove=rm)
