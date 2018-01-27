import click
import docker

from . import exceptions
from .main import main


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def run(args):
    client = docker.from_env()
    try:
        main(client, args)
    except exceptions.MultiContainersFoundError:
        print(
            ("mulitiple containers found,\n"
             "ensure only one container with the `app.rind` label is running"))
    except exceptions.ContainerNotRunning:
        print("No rind enabled container is running")
