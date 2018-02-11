import os

from aloft.process import execute
from aloft import aws
from aloft import k8s
from aloft import chart_config
from aloft import output
from aloft import volume


def apply_charts(release_id, chart_set, charts, sandbox_name=None):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']
    k8s.create_namespace(namespace)

    volume.restore_volumes(release_id, chart_set, charts, sandbox_name)

    for chart in charts:
        value_filenames = chart_config.generate_value_files(release_id, chart_set, chart, release_config)
        secrets_config = chart_config.get_secrets_config_for_chart(chart_set, chart)
        apply_chart(chart, namespace, value_filenames, secrets_config)

    if release_config.get('lockVolumes', False):
        volume.lock_volumes(release_id, chart_set, charts, sandbox_name)


def apply_chart(chart, namespace, value_filenames, secrets_config):
    base_chart_config_directory = chart_config.get_base_chart_config_directory()
    chart_directory = f'{base_chart_config_directory}/charts/{chart}'
    value_args = ' '.join(map(lambda filename: f'-f {filename}', value_filenames))
    release_name = get_release_name(chart, namespace)

    create_secrets(chart, secrets_config, namespace)
    execute_install_hook('pre-install', chart_directory)
    execute(f'helm dependencies build {chart_directory}')
    execute(f'helm upgrade -i {release_name} --namespace {namespace} {chart_directory} {value_args}')
    execute_install_hook('post-install', chart_directory)


def delete_charts(release_id, chart_set, charts, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']

    for chart in charts:
        secrets_config = chart_config.get_secrets_config_for_chart(chart_set, chart)
        delete_chart(chart, namespace, secrets_config)

    k8s.delete_namespace_if_empty(namespace)

    volume.remove_released_volume_resources(release_id, chart_set, charts, sandbox_name)


def delete_chart(chart, namespace, secrets_config):
    base_chart_config_directory = chart_config.get_base_chart_config_directory()
    chart_directory = f'{base_chart_config_directory}/charts/{chart}'
    release_name = get_release_name(chart, namespace)

    execute_install_hook('pre-uninstall', chart_directory)
    execute(f'helm delete --purge {release_name}', ['not found'])
    delete_secrets(chart, secrets_config, namespace)
    execute_install_hook('post-uninstall', chart_directory)


def get_release_name(chart, namespace):
    release_name = chart

    if chart != namespace:
        release_name = f'{namespace}-{chart}'

    return release_name


def create_secrets(chart, secrets_config, namespace):
    secret_args = ''
    secret_keys = []

    if secrets_config:
        for item in secrets_config.get('items', []):
            vault_key = item.get('vaultKey', None)
            secret_key = item.get('secretKey', None)

            if secret_key:
                secret_keys.append(secret_key)
                secret_value = aws.get_secret(vault_key)

                if secret_value:
                    secret_args = f'{secret_args} --from-literal={secret_key}={secret_value}'

        if secret_args:
            secrets_name = secrets_config.get('secretName', f'{chart}-secret')
            output.print_action(f'Creating secret {secrets_name} with keys {secret_keys}')
            execute(f'kubectl -n {namespace} delete secret {secrets_name}', ['NotFound'], quiet=True)
            execute(f'kubectl -n {namespace} create secret generic {secrets_name} {secret_args}', quiet=True)


def delete_secrets(chart, secrets_config, namespace):
    if secrets_config:
        secrets_name = secrets_config.get('secretName', f'{chart}-secret')
        execute(f'kubectl -n {namespace} delete secret {secrets_name}', ['NotFound'])


def execute_install_hook(hook_type, chart_directory):
    hook_script = f'{chart_directory}/hooks/{hook_type}'

    if os.path.exists(hook_script):
        execute(hook_script)
