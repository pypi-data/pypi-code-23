import logging

from pathlib import Path

import click

from opx import config

L = logging.getLogger(config.APP_NAME)


@click.command()
@config.pass_config
def cleanup(c: config.Config) -> None:
    """Remove stale entries from configuration file."""
    L.warning('Deprecation: this command will be removed in the next release.')
    L.warning('No replacement is needed.')

    delete = []
    for r in c._parser:
        L.debug('[cleanup  ] Section: {r}'.format(r=r))
        root = Path(r) / '.repo'
        if not root.exists() and r is not 'DEFAULT':
            delete.append(r)
    for r in delete:
        L.info('Deleting {r} config...'.format(r=r))
        del c._parser[r]
    c.write()
