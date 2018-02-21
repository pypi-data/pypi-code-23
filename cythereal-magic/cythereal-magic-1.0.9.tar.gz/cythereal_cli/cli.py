import click

from .api_client import configure_api
from .upload import upload

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-k', '--key', 'api_key', envvar='MAGIC_API_KEY',
              prompt="MAGIC API Key",
              help="API Key for the MAGIC API. Can be set using the environment variable MAGIC_API_KEY")
def main(api_key):
    configure_api(api_key)

# Add subcommands
main.add_command(upload)


if __name__ == '__main__':
    main()
