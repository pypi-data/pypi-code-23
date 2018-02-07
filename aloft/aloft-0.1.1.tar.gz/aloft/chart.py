import os
from aloft.process import execute
from aloft import k8s
from aloft import chart_config
from aloft import volume


def apply_charts(release_id, chart_set, charts, sandbox_name=None, should_lock_volumes=False):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']
    k8s.create_namespace(namespace)

    volume.restore_volumes(release_id, chart_set, charts, sandbox_name)

    for chart in charts:
        value_filenames = chart_config.generate_value_files(release_id, chart_set, chart, release_config)
        apply_chart(chart, namespace, value_filenames)

    if should_lock_volumes:
        volume.lock_volumes(release_id, chart_set, charts, sandbox_name)


def apply_chart(chart, namespace, value_filenames):
    base_chart_config_directory = chart_config.get_base_chart_config_directory()
    chart_directory = f'{base_chart_config_directory}/charts/{chart}'
    value_args = ' '.join(map(lambda filename: f'-f {filename}', value_filenames))
    release_name = get_release_name(chart, namespace)

    execute_install_hook('pre-install', chart_directory)
    execute(f'helm dependencies build {chart_directory}')
    execute(f'helm upgrade --wait -i {release_name} --namespace {namespace} {chart_directory} {value_args}')
    execute_install_hook('post-install', chart_directory)


def delete_charts(release_id, chart_set, charts, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']

    for chart in charts:
        delete_chart(chart, namespace)

    k8s.delete_namespace_if_empty(namespace)

    volume.remove_released_volume_resources(release_id, chart_set, charts, sandbox_name)


def delete_chart(chart, namespace):
    base_chart_config_directory = chart_config.get_base_chart_config_directory()
    chart_directory = f'{base_chart_config_directory}/charts/{chart}'
    release_name = get_release_name(chart, namespace)

    execute_install_hook('pre-uninstall', chart_directory)
    execute(f'helm delete --purge {release_name}', ['not found'])
    execute_install_hook('post-uninstall', chart_directory)


def get_release_name(chart, namespace):
    release_name = chart

    if chart != namespace:
        release_name = f'{namespace}-{chart}'

    return release_name


def execute_install_hook(hook_type, chart_directory):
    hook_script = f'{chart_directory}/hooks/{hook_type}'

    if os.path.exists(hook_script):
        execute(hook_script)
