import os
import yaml
from aloft import config
from aloft import input
from io import open
from tempfile import NamedTemporaryFile


def get_release_config(chart_set, release_id, sandbox_name):
    release_configs = get_releases_config(chart_set)
    release_config = release_configs[release_id]

    if sandbox_name:
        sandbox_config = release_configs['sandbox']
        sandbox_config['valuesPath'] = release_config['valuesPath']
        sandbox_config['namespace'] += f'-{sandbox_name}'
        release_config = sandbox_config

    add_sandbox_properties(release_config, sandbox_name)

    return release_config


def get_releases_config(chart_set):
    chart_set_config_directory = get_chart_set_config_directory(chart_set)
    with open(f'{chart_set_config_directory}/releases.yaml', 'r') as stream:
        return yaml.load(stream)


def add_sandbox_properties(release_config, sandbox_name):
    if sandbox_name:
        sandbox_name_prefixed_with_dash = f'-{sandbox_name}'
        sandbox_name_suffixed_with_dash = f'{sandbox_name}-'
    else:
        sandbox_name = ''
        sandbox_name_prefixed_with_dash = ''
        sandbox_name_suffixed_with_dash = ''

    if 'properties' not in release_config:
        release_config['properties'] = {}

    release_config['properties']['sandboxName'] = sandbox_name
    release_config['properties']['sandboxNamePrefixedWithDash'] = sandbox_name_prefixed_with_dash
    release_config['properties']['sandboxNameSuffixedWithDash'] = sandbox_name_suffixed_with_dash


def get_charts_to_use(chart_set):
    charts_config = get_charts_config(chart_set)
    charts_to_apply = []

    for chart in charts_config['charts']:
        charts_to_apply.append(chart['name'])

    return charts_to_apply


def get_charts_config(chart_set):
    chart_set_config_directory = get_chart_set_config_directory(chart_set)
    with open(f'{chart_set_config_directory}/charts.yaml', 'r') as stream:
        return yaml.load(stream)


def get_chart_set_config_directory(chart_set):
    base_chart_config_directory = get_base_chart_config_directory()
    return f'{base_chart_config_directory}/chart-sets/{chart_set}'


def get_base_chart_config_directory():
    return config.get_aloft_config_directory()


def generate_value_files(release_id, chart_set, chart, release_config):
    values_config_directory = get_chart_set_config_directory(chart_set)
    value_paths = release_config.get('valuesPath', f'values/{release_id}').split('/')
    properties = release_config['properties']
    value_filenames = []

    for path in value_paths:
        values_config_directory += f'/{path}'
        append_generated_values_file(values_config_directory, chart, properties, value_filenames)

    return value_filenames


def append_generated_values_file(values_config_directory, chart, properties, value_filenames):
    filename = f'{values_config_directory}/{chart}.yaml'

    if os.path.isfile(filename):
        rendered_values = input.render_template_file(filename, properties)
        with NamedTemporaryFile(mode='w+t', encoding='utf-8', delete=False) as temp_file:
            temp_file.write(rendered_values)
            temp_file.write('\n')
            value_filenames.append(temp_file.name)