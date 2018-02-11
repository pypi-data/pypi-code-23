"""
kubic-ci command line interface called `kubic`.

See:
    setup.py
"""
import argparse

from ci3.commands.base import CommandLineInterface, CliCommand
from ci3.commands.dotci3 import StatusCommand, InitCommand, ShowCommand
from ci3.commands.k8s import ApplyCommand, AccessCommand, DeployCommand
from ci3.commands.dkr import BuildCommand, PushCommand
from ci3.commands.gke import GkeCommand
from ci3.version import __version__


BOX = u'\u2B1C'
PROMPT = u'{box}: kubic CI {version}'.format(box=BOX, version=__version__)


class RedoCommand(CliCommand):
    """Shorthand for `kubic build && kubic push && kubic deploy`."""

    def run(self, args):
        """Chain three commands."""
        BuildCommand().run(args)
        PushCommand().run(args)
        DeployCommand().run(args)


def main():
    """Entry point for the CLI."""
    # Print prompt at the start, always.
    parser = argparse.ArgumentParser(description=PROMPT)
    cli = CommandLineInterface(parser)

    # Add arguments shared between commands.
    cli.parser.add_argument('-v', '--verbose', dest='verbose',
                            action='count', default=1)

    # Add commands with respective subcommands. See run method of each class.
    cli.add_command('status', StatusCommand)
    cli.add_command('init', InitCommand)
    cli.add_command('show', ShowCommand)
    cli.add_command('apply', ApplyCommand)
    cli.add_command('access', AccessCommand)
    cli.add_command('build', BuildCommand)
    cli.add_command('push', PushCommand)
    cli.add_command('deploy', DeployCommand)
    cli.add_command('redo', RedoCommand)
    # TODO: implement
    # cli.add_command('gke', GkeCommand)

    # Parse cli arguments and execute respective command to handle them.
    cli.run()
