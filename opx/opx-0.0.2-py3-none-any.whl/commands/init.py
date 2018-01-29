import logging

from pathlib import Path
from typing import Tuple

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command(help='Initialize an OpenSwitch workspace.')
@click.option('-u', default=config.OPX_MANIFEST,
              help='Manifest repository URL')
@click.option('-m', default='default.xml',
              help='Manifest file within repository')
@click.option('-b', default='master',
              help='Branch of repository to use')
@click.argument('projects', nargs=-1,)
@config.pass_config
def init(c: config.Config, u: str, m: str, b: str, projects: Tuple[str]) -> None:
    if str(Path().cwd()) not in c.parser.sections():
        c.parser[Path().cwd()] = {}
        cmd = f'repo init -u {u} -m {m} -b {b}'
        run.noninteractive(cmd, 'Initializing repositories...')
        cmd = f'repo sync {" ".join(projects)}'
        run.noninteractive(cmd, 'Synchronizing repositories...')
        c.write()
    else:
        L.info('Repositories already initialized. To update repositories, run `repo sync`.')