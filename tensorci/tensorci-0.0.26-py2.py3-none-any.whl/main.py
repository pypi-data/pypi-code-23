import click
from commands import all_cmds

# Allow '-h' to be an alias of '--help'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# 'tensorci' entrypoint
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
  pass


# Attach all commands to the CLI
[cli.add_command(cmd) for cmd in all_cmds]