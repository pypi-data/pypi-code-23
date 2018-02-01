"""Run shell commands interactively or non-interactively"""

import logging
import os
import sys
import time

from pathlib import Path

import delegator
import docker
import dockerpty

from halo import Halo

from opx import config
from opx.exceptions import CommandException

L = logging.getLogger(config.APP_NAME)


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def noninteractive(cmd: str, msg: str) -> None:
    """Run a non-interactive command."""
    # remove extra whitespace in command
    cmd = ' '.join(cmd.split())
    L.debug('[running  ] {cmd}'.format(cmd=cmd))
    with Halo(text=msg):
        c = delegator.run(cmd)
    L.debug('[stdout   ] {out}'.format(out=c.out))

    if c.return_code != 0:
        L.error('[stderr   ] {err}'.format(err=c.err))
        raise CommandException(cmd, c.return_code)


def _create_container(client: docker.APIClient,
                      dist: str = 'unstable',
                      mnt_dir: Path = Path().cwd(),
                      cmd: str = 'bash') -> docker.DockerClient.containers:
    image = 'opxhub/build:{dist}'.format(dist=dist)

    L.debug('[container] Creating new container!')
    L.debug('[container] Mounting {dir} to /mnt'.format(dir=mnt_dir))

    return client.containers.create(
        image=image,
        auto_remove=False,
        detach=False,
        environment={
            'LOCAL_UID': os.getuid(),
            'LOCAL_GID': os.getgid(),
            'OPX_POOL_PACKAGES': os.getenv('OPX_POOL_PACKAGES'),
            'OPX_GIT_TAG': os.getenv('OPX_GIT_TAG'),
        },
        privileged=True,
        stdin_open=True,
        tty=_is_interactive(),
        volumes={
            mnt_dir: {'bind': '/mnt', 'mode': 'rw'},
            str(Path.home() / '.gitconfig'): {'bind': '/home/opx/.gitconfig', 'mode': 'ro'},
            '/etc/localtime': {'bind': '/etc/localtime', 'mode': 'ro'},
        },
        command=cmd,
    )


def in_container(c: config.Config, dist: str = 'unstable', remove: bool = True, cmd: str = None) -> None:
    """Run a command inside a docker container.

    If no command is specified, an interactive shell is launched.
    """
    client = docker.from_env()

    image = 'opxhub/build:{dist}'.format(dist=dist)
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        L.warning('{image} not found!'.format(image=image))
        L.warning('Pulling {image}...'.format(image=image))
        client.images.pull(image)

    mnt_dir = c.root if c.root else Path().cwd()

    if c.config is None or 'containerID' not in c.config:
        container = _create_container(
            client=client,
            dist=dist,
            mnt_dir=mnt_dir,
            cmd='bash',
        )
        if c.config is not None:
            c.config['containerID'] = container.id
            c.write()
    else:
        try:
            container = client.containers.get(c.config['containerID'])
        except docker.errors.NotFound:
            L.warning('Container {id} not found.'.format(id=c.config['containerID']))
            del c.config['containerID']

            container = _create_container(
                client=client,
                dist=dist,
                mnt_dir=mnt_dir,
                cmd='bash',
            )
            c.config['containerID'] = container.id
            c.write()

    L.debug('[container] Starting container {id}'.format(id=container.id))
    if cmd:
        L.debug('[command  ] {cmd}'.format(cmd=cmd))

    container.start()
    # let entrypoint run and user get created
    time.sleep(0.1)

    cmd = 'sudo -u opx bash -c ". ~/.bashrc; {cmd}"'.format(cmd=cmd) if cmd else 'sudo -u opx bash'
    dockerpty.exec_command(client.api, container.id, command=cmd)

    if c.config is None or remove:
        L.debug('[container] Stopping container {id}'.format(id=container.id))
        container.stop()
        L.debug('[container] Removing container {id}'.format(id=container.id))
        container.remove()
        if c.config is not None and 'containerID' in c.config:
            del c.config['containerID']
            c.write()
