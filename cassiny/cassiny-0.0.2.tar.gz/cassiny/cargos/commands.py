import sys

import click
from terminaltables import AsciiTable

from ..utils import make_request


@click.group()
def cargo():
    """Cargos cli."""
    pass


@cargo.command('create', short_help='create a new cargo.')
@click.option('--description', '-d', help="Description", default=None)
@click.option('--size', '-s', help="Size in giga", default=10, type=int)
def create(description, size):
    """Create a new cargo."""
    if description is None:
        click.echo("A description is needed.")
        sys.exit(1)

    data = {
        "description": description,
        "size": size,
    }
    response = make_request('/api/spawner/cargos', method='POST', data=data)
    click.echo(response.json()['message'])


@cargo.command()
def list():
    """List your cargos."""
    response = make_request('/api/spawner/cargos', method='GET')
    cargos = response.json()["cargos"]

    data = []
    data.append(["", "Name", "Url", "Size", "Access key", "Secret Key"])
    for index, cargo in enumerate(cargos):
        data.append([
            index, cargo['name'], cargo['url'], cargo['size'],
            cargo['specs']['access_key'], cargo['specs']['secret_key']
        ])
    table = AsciiTable(data)
    table.inner_row_border = True
    click.echo(table.table)


@cargo.command()
@click.argument('name')
def remove(name):
    """Remove a cargo."""
    uri = '/api/spawner/cargos/{}'.format(name)
    response = make_request(uri, method='DELETE')
    click.echo(response.json()['message'])
