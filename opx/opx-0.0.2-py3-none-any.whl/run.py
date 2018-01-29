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
from opx.exceptions import CliException

L = logging.getLogger(config.APP_NAME)


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def noninteractive(cmd: str, msg: str) -> None:
    """Run a non-interactive command."""
    # remove extra whitespace in command
    cmd = ' '.join(cmd.split())
    L.debug(f'[running  ] {cmd}')
    with Halo(text=msg):
        c = delegator.run(cmd)
    L.debug(f'[stdout   ] {c.out}')

    if c.return_code != 0:
        L.error(f'[stderr   ] {c.err}')
        raise CliException(cmd, c.return_code)


def _create_container(
        client: docker.APIClient,
        dist: str = 'unstable',
        mnt_dir: Path = Path().cwd(),
        cmd: str = 'bash'
) -> docker.DockerClient.containers:
    image = f'opxhub/build:{dist}'

    L.debug('[container] Creating new container!')
    L.debug(f'[container] Mounting {mnt_dir} to /mnt')

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

    image = f'opxhub/build:{dist}'
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound as e:
        L.info(f'{image} not found!')
        L.info(f'Pulling {image}...')
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
            L.warning(f'Container {c.config["containerID"]} not found.')
            del c.config['containerID']

            container = _create_container(
                client=client,
                dist=dist,
                mnt_dir=mnt_dir,
                cmd='bash',
            )
            c.config['containerID'] = container.id
            c.write()

    L.debug(f'[container] Starting container {container.id}')
    if cmd:
        L.debug(f'[command  ] {cmd}')

    container.start()
    # let entrypoint run and user get created
    time.sleep(0.1)

    cmd = f'sudo -u opx bash -c ". ~/.bashrc; {cmd}"' if cmd else 'sudo -u opx bash'
    dockerpty.exec_command(client.api, container.id, command=cmd)

    if c.config is None or remove:
        L.debug(f'[container] Stopping container {container.id}')
        container.stop()
        L.debug(f'[container] Removing container {container.id}')
        container.remove()
        if c.config is not None and 'containerID' in c.config:
            del c.config['containerID']
            c.write()