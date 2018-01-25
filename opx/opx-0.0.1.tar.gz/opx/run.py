"""Run shell commands interactively or non-interactively"""

import logging
import os
import sys

from pathlib import Path

import delegator
import docker
import dockerpty

from halo import Halo

from .exceptions import CliException

L = logging.getLogger('opx')


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def noninteractive(cmd: str, msg: str) -> None:
    """Run a non-interactive command."""
    # remove extra whitespace in command
    cmd = ' '.join(cmd.split())
    L.debug(f'[running] {cmd}')
    with Halo(text=msg):
        c = delegator.run(cmd)
    L.debug(f'[stdout]  {c.out}')

    if c.return_code != 0:
        L.error(f'[stderr]  {c.err}')
        raise CliException(cmd, c.return_code)


def in_container(rm: bool, cmd: str = None) -> None:
    """Run a command inside a docker container.

    If no command is specified, an interactive shell is launched.
    """
    client = docker.from_env()

    image = 'opxhub/build'
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound as e:
        L.info(f'{image} not found!')
        L.info(f'Pulling {image}...')
        client.images.pull(image)

    container = client.containers.create(
        image=image,
        auto_remove=rm,
        detach=False,
        environment={
            'LOCAL_UID': os.getuid(),
            'LOCAL_GID': os.getgid(),
            'OPX_POOL_PACKAGES': os.getenv('OPX_POOL_PACKAGES'),
            'OPX_GIT_TAG': os.getenv('OPX_GIT_TAG'),
        },
        privileged=True,
        stdin_open=True,
        tty=is_interactive(),
        volumes={
            os.getcwd(): {'bind': '/mnt', 'mode': 'rw'},
            str(Path.home() / '.gitconfig'): {'bind': '/home/opx/.gitconfig', 'mode': 'ro'},
        },
        command=f'sh -c "{cmd}"' if cmd else 'bash',
    )

    L.debug(f'[container] {container.id}')
    if cmd:
        L.debug(f'[command]   {cmd}')

    dockerpty.start(client.api, container.id)
