import click
from .commands.create import create
from .commands.users import users

@click.group()
def cli():
    pass

cli.add_command(create)
cli.add_command(users)
#entry_point.add_command(group2.version)    