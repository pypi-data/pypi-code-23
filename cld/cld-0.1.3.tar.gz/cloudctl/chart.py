import os
import yaml
from io import open
from tempfile import NamedTemporaryFile
from cloudctl.process import execute
from cloudctl.cluster import use_cluster, create_namespace, delete_namespace
from cloudctl.input import get_directory_from_environment, render_template_file


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
    return get_directory_from_environment('K8S_CHART_CONFIG')


def apply_charts(release_id, chart_set, charts, sandbox_name):
    release_config = get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']
    use_cluster(release_config['cluster'])
    create_namespace(namespace)

    for chart in charts:
        # TODO: Apply any persistent volume config files
        # kubectl apply -f "$releaseConfigsDirectory/"

        value_filenames = generate_value_files(release_id, chart_set, chart, release_config)
        apply_chart(chart, namespace, value_filenames)

        # TODO: Lock volumes if option is set
        # if [ "$lockVolumes" = "true" ]; then
        # ./lock-volumes $releaseId $chartSetName $chart
        # fi


def add_sandbox_properties(release_config, sandbox_name):
    if sandbox_name:
        sandbox_name_prefixed_with_dash = f'-{sandbox_name}'
        sandbox_name_suffixed_with_dash = f'{sandbox_name}-'
    else:
        sandbox_name = ''
        sandbox_name_prefixed_with_dash = ''
        sandbox_name_suffixed_with_dash = ''

    release_config['properties']['sandboxName'] = sandbox_name
    release_config['properties']['sandboxNamePrefixedWithDash'] = sandbox_name_prefixed_with_dash
    release_config['properties']['sandboxNameSuffixedWithDash'] = sandbox_name_suffixed_with_dash


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
        rendered_values = render_template_file(filename, properties)
        with NamedTemporaryFile(mode='w+t', encoding='utf-8', delete=False) as tmp:
            tmp.write(rendered_values)
            tmp.write('\n')
            value_filenames.append(tmp.name)


def apply_chart(chart, namespace, value_filenames):
    base_chart_config_directory = get_base_chart_config_directory()
    chart_directory = f'{base_chart_config_directory}/charts/{chart}'
    value_args = ' '.join(map(lambda filename: f'-f {filename}', value_filenames))

    execute(f'helm dependencies build {chart_directory}')
    execute(f'helm upgrade --wait -i {namespace}-{chart} --namespace {namespace} {chart_directory} {value_args}')


def delete_charts(release_id, chart_set, charts, sandbox_name):
    release_config = get_release_config(chart_set, release_id, sandbox_name)
    use_cluster(release_config['cluster'])

    for chart in charts:
        delete_chart(chart, release_config['namespace'])

    delete_namespace_if_empty(release_config['namespace'])


def delete_chart(chart, namespace):
    execute(f'helm delete --purge {namespace}-{chart}', ['not found'])

    # TODO: delete PV if volume lock config file exists
    # volumeLockFile="$releaseConfigsDirectory/$chart-pv.yaml"
    #
    # if [ -f $volumeLockFile ]; then
    #     kubectl delete -f $volumeLockFile
    # fi


def delete_namespace_if_empty(namespace):
    releases = get_releases_by_namespace(namespace)

    if not releases:
        delete_namespace(namespace)


def get_releases_by_namespace(namespace):
    output = execute(f'helm ls -q --namespace {namespace}')
    return output.splitlines()
