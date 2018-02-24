"""

quoteBot.py
~~~~~~~~

Driving module of quoteBot.

Provides the driver logic of quoteBot and is the main entry point of the
script.


TODO: implement oauth check for whether a user has a auth.py file or if
registering will be necessary via auth command.

TODO: get basic parser implemented

TODO: get basic tweeting ability implemented

:copyright: @ 2018
:author: elias julian marko garcia
:license: MIT, see LICENSE
"""
import click

from quoteBot.commands.parser import extractPDF, extractTXT
from quoteBot.commands.authenticate import authenticate


@click.group()
@click.option('--verbose', is_flag=True, help='verbose output')
def cli(verbose):
    """quoteBot is a CLI tool to help you create text quote bots for twitter

    :param cmd: the command for quoteBot to execute

    """
    if verbose:
        click.echo("very verbose output")
    pass
    # parse(cmd)


cli.add_command(extractTXT)
cli.add_command(extractPDF)
cli.add_command(authenticate)
