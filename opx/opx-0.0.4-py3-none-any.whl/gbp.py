"""Builds Debian packages from git repositories in a Docker container"""

import logging

from opx import config
from opx import run

L = logging.getLogger(config.APP_NAME)


def buildpackage(c: config.Config, dir: str, dist='unstable', rm=False, sort=False, tag=False):
    cmd = 'opx_build {dir}'.format(dir=dir)

    if sort:
        cmd = 'OPX_POOL_PACKAGES=yes {cmd}'.format(cmd=cmd)

    if tag:
        cmd = 'OPX_GIT_TAG=yes {cmd}'.format(cmd=cmd)

    run.in_container(
        c=c,
        dist=dist,
        remove=rm,
        cmd=cmd
    )
