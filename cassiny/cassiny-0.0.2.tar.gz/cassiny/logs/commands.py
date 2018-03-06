import click

from ..utils import make_request


@click.group()
def logs():
    """Get service logs."""
    pass


@logs.command()
@click.argument('name')
def get(name):
    """Get logs of a probe, api or job."""
    uri = '/api/spawner/logs/{}'.format(name)
    response = make_request(uri, method='GET')

    click.echo(response.json()['logs'])
