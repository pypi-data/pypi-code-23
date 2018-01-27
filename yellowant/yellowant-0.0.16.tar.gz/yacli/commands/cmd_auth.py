"""Save the authentication detaisl to the config file"""
import ConfigParser
import click
from yacli.cli import pass_context


def save_token(token, host, config_file):
    """Write token and host configs to a file"""
    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    if not config.has_section("YELLOWANT_DEV"):
        config.add_section('YELLOWANT_DEV')
    config.set('YELLOWANT_DEV', 'token', token)
    config.set("YELLOWANT_DEV", "host", host)
    with open(config_file, 'wb') as configfile:
        config.write(configfile)

    return token

@click.command()
@click.option('--token',
              hide_input=True,
              prompt='YellowAnt developer token',
              help="YellowAnt developer token.")
@click.option('--host',
              default="https://www.yellowant.com",
              prompt="YellowAnt Host URL",
              help="YellowAnt server host url.")
@pass_context
def cli(ctx, token, host):
    """Permanently save YellowAnt authentication details to a config file."""
    save_token(token, host, ctx.config_file)
