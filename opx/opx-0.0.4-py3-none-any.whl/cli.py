import click
import click_completion
import click_log

from opx import config
from opx.commands import (
    assemble, build, cleanup, init, release, remove, shell, status,
)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

click_completion.init()
click_log.basic_config(config.APP_NAME)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(prog_name='OpenSwitch Development Tool')
@click_log.simple_verbosity_option(config.APP_NAME)
@click.pass_context
def opx(ctx) -> None:
    ctx.obj = config.Config()
    if ctx.obj.config is not None and ctx.obj.config.get('dist') is None:
        ctx.obj.config['dist'] = 'unstable'


opx.add_command(assemble)
opx.add_command(build)
opx.add_command(cleanup)
opx.add_command(init)
opx.add_command(release)
opx.add_command(remove)
opx.add_command(shell)
opx.add_command(status)
