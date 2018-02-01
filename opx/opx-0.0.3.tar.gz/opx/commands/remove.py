import logging

import click

from opx import config
from opx import run
from opx.exceptions import CliException

L = logging.getLogger(config.APP_NAME)


@click.command(help='Remove current workspace container.')
@config.pass_config
def remove(c: config.Config) -> None:
    if c.root is None:
        raise CliException('Must be inside a repository root.')

    cid = c.config.get('containerID')

    if cid is None:
        raise CliException('No container is running.')

    L.debug('[remove   ] Removing {cid}...'.format(cid=cid))
    run.noninteractive('docker stop {cid}'.format(cid=cid), 'Stopping {cid}...'.format(cid=cid))
    run.noninteractive('docker rm -f {cid}'.format(cid=cid), 'Stopping {cid}...'.format(cid=cid))
    del c.config['containerID']
    c.write()
