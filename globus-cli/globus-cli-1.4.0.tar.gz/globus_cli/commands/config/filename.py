import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.config import get_config_obj


@click.command('filename', help='Output the path of the config file')
@common_options(no_format_option=True, no_map_http_status_option=True)
def filename_command():
    """
    Executor for `globus config filename`
    """
    try:
        config = get_config_obj(file_error=True)
    except IOError as e:
        safeprint(e, write_to_stderr=True)
        click.get_current_context().exit(1)
    else:
        safeprint(config.filename)
