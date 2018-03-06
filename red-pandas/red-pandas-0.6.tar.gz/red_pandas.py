import click

from utils.pandas_utils import message


@click.group()
@click.version_option(prog_name='Cloud Pipeline CLI')
def cli():
    """pipe is command line interface to Bfx Pipeline engine
    It allows run pipelines as well as viewing runs and cluster state
    """
    pass


@cli.command()
@click.option('-n', '--name',
              help='Red panda name',
              default='Yo')
def print_message(name):
    """Configures CLI parameters
    """
    print "Aloha pussies!"
    message(name)
