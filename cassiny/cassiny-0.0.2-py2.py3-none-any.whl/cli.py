import click

from . import config as c
from .apis import api
from .auth import login, logout, signup
from .blueprints import blueprint
from .cargos import cargo
from .jobs import job
from .logs import logs
from .probes import probe


@click.group()
@click.option('-h', '--host', default='https://mcc.cassiny.io', help='URL of cassiny server.')
def cli(host):
    """
    CLI to interact with Cassiny's servers and execute your commands.
    """
    c.BASE_URI = host


def add_commands(cli):
    cli.add_command(login)
    cli.add_command(logout)
    cli.add_command(signup)

    cli.add_command(logs)
    cli.add_command(probe)
    cli.add_command(cargo)
    cli.add_command(api)
    cli.add_command(blueprint)
    cli.add_command(job)


add_commands(cli)
