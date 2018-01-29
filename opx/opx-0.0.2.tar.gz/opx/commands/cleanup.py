import logging

from pathlib import Path

import click

from opx import config

L = logging.getLogger(config.APP_NAME)


@click.command(help='Remove stale entries from configuration file')
@config.pass_config
def cleanup(c: config.Config) -> None:
    delete = []
    for r in c.parser:
        L.debug(f'[cleanup  ] Section: {r}')
        root = Path(r) / '.repo'
        if not root.exists() and r is not 'DEFAULT':
            delete.append(r)
    for r in delete:
        L.info(f'Deleting {r} config...')
        del c.parser[r]
    c.write()