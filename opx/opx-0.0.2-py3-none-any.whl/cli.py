import click
import click_completion
import click_log

from opx import config
from opx.commands import (
    assemble, build, cleanup, init, remove, shell, status,
)

click_completion.init()
click_log.basic_config(config.APP_NAME)


@click.group()
@click_log.simple_verbosity_option(config.APP_NAME)
@click.pass_context
def opx(ctx) -> None:
    ctx.obj = config.Config()


opx.add_command(assemble)
opx.add_command(build)
opx.add_command(cleanup)
opx.add_command(init)
opx.add_command(remove)
opx.add_command(shell)
opx.add_command(status)