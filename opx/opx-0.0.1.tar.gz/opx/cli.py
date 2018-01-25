import logging

from typing import Tuple

import click
import click_completion
import click_log

from . import run

click_completion.init()

L = logging.getLogger('opx')
click_log.basic_config('opx')

OPX_MANIFEST = 'git://git.openswitch.net/opx/opx-manifest'


@click.group()
@click_log.simple_verbosity_option('opx')
def opx() -> None:
    pass


@opx.command(help='Initialize an OpenSwitch workspace.')
@click.option('-u', default=OPX_MANIFEST,
              help='Manifest repository URL')
@click.option('-m', default='default.xml',
              help='Manifest file within repository')
@click.option('-b', default='master',
              help='Branch of repository to use')
@click.argument('projects', nargs=-1,)
def init(u: str, m: str, b: str, projects: Tuple[str]) -> None:
    cmd = f'repo init -u {u} -m {m} -b {b}'
    run.noninteractive(cmd, 'Initializing repositories...')
    cmd = f'repo sync {" ".join(projects)}'
    run.noninteractive(cmd, 'Synchronizing repositories...')


@opx.command(help='Build one or more repositories.')
@click.argument('repos', nargs=-1)
def build(repos: Tuple[str]) -> None:
    if len(repos) == 0:
        # trailing comma creates single item tuple
        repos = "all",
    for repo in repos:
        run.in_container(rm=True, cmd=f'opx_build {repo}')


@opx.command(help='Launch a shell for building OPX packages.')
@click.option('--rm/--no-rm', default=True, help='Remove container on exit.')
def shell(rm: bool) -> None:
    run.in_container(rm=rm)
