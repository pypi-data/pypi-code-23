import base64
import os

from libcloud.compute.types import Provider
from pkg_resources import get_distribution

import click
from cookiecutter.main import cookiecutter

DIST = get_distribution('sbcloud')


@click.group()
@click.version_option()
def main():
    pass


@main.command()
@click.option(
    '--vendor',
    required=True
)
@click.option(
    '--product',
    required=True
)
@click.option(
    '--provider',
    required=True
)
@click.option(
    '--logo-path',
    type=click.Path(exists=True, dir_okay=False),
    required=True
)
@click.option(
    '--version',
    default='1.0.0'
)
def generate(**kwargs):
    cc_path = os.path.join(os.path.dirname(__file__), 'cookiecutter')

    kwargs['sbcloud_version'] = DIST.version
    kwargs['project_name'] = _get_project_name(kwargs['vendor'], kwargs['product'])
    kwargs['project_slug'] = _get_project_slug(kwargs['project_name'])
    kwargs['asset_name'] = _get_asset_name(kwargs['project_name'])
    kwargs['logo_base64'] = _get_logo_base64(kwargs['logo_path'])

    if not hasattr(Provider, kwargs['provider']):
        raise ValueError('Unknown libcloud compute provider "{}"'.format(kwargs['provider']))

    cookiecutter(cc_path, no_input=True, extra_context=kwargs)


def _get_logo_base64(logo_path):
    """Read in logo file and convert to base 64 URI"""
    with open(logo_path, 'rb') as f:
        base64_content = base64.b64encode(f.read())

    return 'data:image/{};base64,{}'.format(
        os.path.splitext(logo_path)[1][1:],
        base64_content
    )


def _get_project_name(vendor, product):
    """Return readable project name"""
    if vendor == product:
        return vendor
    else:
        return ' '.join([vendor, product])


def _get_project_slug(project_name):
    """Return python-importable project slug name"""
    return project_name.lower().replace(' ', '_')


def _get_asset_name(project_name):
    return project_name.replace(' ', '')
