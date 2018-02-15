import logging

import click

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


@click.command()
@click.option('-b', default='opx-onie-installer/release_bp/OPX_dell_base.xml',
              help='Installer blueprint to use')
@click.option('-n', default=9999,
              help='Release number')
@click.option('-s', default='',
              help='Release suffix')
@click.option('--dist',
              help='Change OPX distribution to build against.')
@click.option('--rm', is_flag=True,
              help='Remove container when command exits.')
@config.pass_config
def assemble(c: config.Config, b, n, s, dist: str, rm: bool) -> None:
    """Assemble an OpenSwitch ONIE installer.

    Local packages always have the highest priority. If packages are not found locally,
    they are pulled from the chosen DIST on deb.openswitch.net.
    The DIST chosen is used in the image for package updates.

    Examples:

    opx assemble

        Create an ONIE installer. Installer will have version "unstable.9999".
        Packages will be pulled from 'http://deb.openswitch.net/ unstable main'

    opx assemble --dist testing -n 5

        Create an ONIE installer. Installer will have version "testing.5".
        Packages will be pulled from 'http://deb.openswitch.net/ testing main'

    opx assemble --dist 2.2.0 -n 0

        Create an ONIE installer. Installer will have version "2.2.0".
        Packages will be pulled from 'http://deb.openswitch.net/ 2.2.0 main'
   """
    dist = c.get_dist(dist)

    cmd = 'opx_rel_pkgasm.py -b {b} -n {n} --dist {dist}'.format(b=b, n=n, dist=dist)
    if s != "":
        cmd += ' -s {s}'.format(s=s)

    run.in_container(c=c, dist=dist, remove=rm, cmd=cmd)
