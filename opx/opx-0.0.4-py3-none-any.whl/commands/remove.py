import logging

import click
import docker

from opx import config
from opx import run
from opx.exceptions import CliException

L = logging.getLogger(config.APP_NAME)


@click.command()
@config.pass_config
def remove(c: config.Config) -> None:
    """Remove container from current workspace."""
    if c.root is None:
        raise CliException('Must be inside a repository root.')

    cid = c.config.get('containerID')

    if cid is None:
        raise CliException('No container is running.')

    L.debug('[remove   ] Removing {cid}...'.format(cid=cid))
    client = docker.from_env()
    container = client.containers.get(cid)
    container.remove(force=True)
    del c.config['containerID']
    c.write()
