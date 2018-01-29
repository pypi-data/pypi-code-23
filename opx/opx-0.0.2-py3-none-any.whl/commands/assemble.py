import logging

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command(help='Assemble an installer.')
@click.option('-b', default='opx-onie-installer/release_bp/OPX_dell_base.xml',
              help='Installer blueprint to use')
@click.option('-n', default=9999,
              help='Release number')
@click.option('-s', default='',
              help='Release suffix')
@click.option('--dist', default='unstable',
              help='OPX distribution to build against.')
@click.option('--remove-container', is_flag=True,
              help='Remove container when command exits.')
@config.pass_config
def assemble(c: config.Config, b, n, s, dist: str, remove_container: bool) -> None:
    cmd = f'opx_rel_pkgasm.py -b {b} -n {n} --dist {dist}'
    if s != "":
        cmd += f' -s {s}'

    run.in_container(c=c, dist=dist, remove=remove_container, cmd=cmd)