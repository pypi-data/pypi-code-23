import click
from lantern_cli import templates


@click.group()
def cli():
	"""
    \b
             * * * * * * * * * * * * * * *
             *                           * 
             *    Lantern Engine CLI     * 
             *                           *
             * * * * * * * * * * * * * * *
	\b
    This tool is for internal user
    in Lantern.tech.
    \b
    "Happy Coding!"
    """
	pass


@cli.command()
def startapp():
	"""Create a new MicroService project \n\n
	   Check the generated README file (project root) for docker instructions. \n
	   Usage:
	   \n\t\t lantern-cli startapp [APP_NAME]
	"""
	templates.startapp()