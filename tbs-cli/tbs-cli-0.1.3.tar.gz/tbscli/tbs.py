import os
import click
import pkgutil
import command_groups
import logging.config
from importlib import import_module
from command_groups import login
from tbscli.CONSTANTS import CLICK_CONTEXT_SETTINGS

logging.config.fileConfig("logging.conf")
tbslog = logging.getLogger('tbs')


class ThreeBladesCLI(click.Group):
    def list_commands(self, ctx):
        commands = ["login"]
        for _, modname, ispkg in pkgutil.iter_modules(command_groups.__path__):
            if not ispkg:
                cmd_name = modname
                commands.append(cmd_name)
        commands.sort()
        return commands

    def get_command(self, ctx, cmd_name):
        if cmd_name != "login":
            module = import_module(f"command_groups.{cmd_name}")
            cmd_group = getattr(module, cmd_name.title() + "CLI")()
            return cmd_group
        else:
            return login


my_cli = ThreeBladesCLI(help="3Blades Command Line Tool", context_settings=CLICK_CONTEXT_SETTINGS)


def main():
    try:
        return my_cli()
    except Exception as e:
        click.echo("Uh oh, something went wrong:")
        click.secho(str(e), fg="red", bold=True)
        click.secho(f"To view the entire stacktrace for debugging, check the "
                    f"logs at {os.getenv('HOME') + '/.threeblades.log'}", fg="yellow")
        tbslog.exception(e)
