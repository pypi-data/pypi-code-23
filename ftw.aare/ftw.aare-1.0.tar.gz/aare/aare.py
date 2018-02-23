import click
import requests


@click.command()
def aare():
    """A simple command which displays the current aare temperature"""
    api_url = 'http://aare.schwumm.ch/aare.json'
    response = requests.get(api_url)
    aare_json = response.json()
    click.echo("Current temperature of the aare: {}C°".format(aare_json["temperature"]))


if __name__ == '__main__':
    aare()
