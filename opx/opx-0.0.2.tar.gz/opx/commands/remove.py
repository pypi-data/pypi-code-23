import logging

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command(help='Remove current workspace container.')
@config.pass_config
def remove(c: config.Config) -> None:
    cid = c.config.get('containerID')

    if cid is not None:
        L.debug(f'[remove   ] Removing {cid}...')
        run.noninteractive(f'docker stop {cid}', f'Stopping {cid}...')
        run.noninteractive(f'docker rm -f {cid}', f'Stopping {cid}...')
        del c.config['containerID']
        c.write()
    else:
        L.info('No container is running.')