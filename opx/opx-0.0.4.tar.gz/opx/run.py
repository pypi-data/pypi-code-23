"""Run shell commands interactively or non-interactively"""

import logging
import os
import platform
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


def in_container(c: config.Config, dist: str = 'unstable', remove: bool = True, cmd: str = None) -> None:
    """Run a command inside a docker container.

    If no command is specified, an interactive shell is launched.
    """
    client = docker.from_env()

    image = 'opxhub/build:{dist}'.format(dist=dist)
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        L.warning('{image} not found! Pulling image...'.format(image=image))
        client.images.pull(image)

    mnt_dir = c.root if c.root else Path().cwd()

    if c.config is None or 'containerID' not in c.config:
        L.debug('[container] Creating new container!')
        L.debug('[container] Mounting {dir} to /mnt'.format(dir=mnt_dir))

        # collect volumes to mount
        volumes = {mnt_dir: {'bind': '/mnt', 'mode': 'rw'}}

        gitconfig = Path.home() / '.gitconfig'
        if gitconfig.exists():
            volumes.update({str(gitconfig): {'bind': '/home/opx/.gitconfig', 'mode': 'ro'}})

        if platform.system() == 'Darwin':
            localtime = Path('/private/etc/localtime')
            if localtime.exists():
                volumes.update({str(localtime.resolve()): {'bind': '/etc/localtime', 'mode': 'ro'}})
        elif platform.system() == 'Linux':
            localtime = Path('/etc/localtime')
            if localtime.exists():
                volumes.update({str(localtime.resolve()): {'bind': '/etc/localtime', 'mode': 'ro'}})

        container = client.containers.create(
            image=image,
            auto_remove=False,
            detach=False,
            environment={
                'LOCAL_UID': os.getuid(),
                'LOCAL_GID': os.getgid(),
            },
            privileged=True,
            stdin_open=True,
            tty=_is_interactive(),
            volumes=volumes,
            command='bash',
        )

        if c.config is not None:
            # we are in a workspace, save container id
            c.config['containerID'] = container.id
            c.write()
    else:
        container = client.containers.get(c.config['containerID'])
        if not any(dist in t for t in container.image.tags):
            L.warning('You previously saved a different distribution for this workspace.')
            L.warning('If you mean to change it, please run `opx remove` and rerun this command.')
            return

    L.debug('[container] Starting container {}'.format(container.name))
    if cmd:
        L.debug('[command  ] {cmd}'.format(cmd=cmd))

    try:
        container.start()
    except docker.errors.APIError as e:
        L.error('Failed to start container.')
        L.error(e.explanation)
        L.debug('Removing created container {}.'.format(container.name))
        container.remove()
        sys.exit(1)

    # let entrypoint run and user get created
    time.sleep(0.1)

    if cmd:
        cmd = 'sudo -u opx bash --login -c "{cmd}"'.format(cmd=cmd)
    else:
        cmd = 'sudo -u opx bash'
    dockerpty.exec_command(client.api, container.id, command=cmd)

    if c.config is None or remove:
        L.debug('[container] Stopping container {id}'.format(id=container.id))
        container.stop()
        L.debug('[container] Removing container {id}'.format(id=container.id))
        container.remove()
        if c.config is not None and 'containerID' in c.config:
            del c.config['containerID']
            c.write()
