import yaml
from aloft.process import execute


def apply_file(filename):
    execute(f'kubectl apply -f {filename}')


def create_namespace(namespace):
    execute(f'kubectl create namespace {namespace}', ['AlreadyExists'])


def delete_namespace_if_empty(namespace):
    releases = get_releases_by_namespace(namespace)

    if not releases:
        delete_namespace(namespace)


def delete_namespace(namespace):
    execute(f'kubectl delete namespace {namespace}', ['NotFound'])


def use_namespace(namespace):
    execute(f'kubectl config set-context $(kubectl config current-context) --namespace={namespace}')


def get_releases_by_namespace(namespace):
    stdout = execute(f'helm ls -q --namespace {namespace}')
    return stdout.splitlines()


def get_resource_by_name(resource_type, resource_name, namespace=None):
    resource = None
    resources = get_resources(resource_type, namespace, None, resource_name)

    if len(resources) == 1:
        resource = resources[0]

    return resource


def get_resources(resource_type, namespace=None, label_selectors=None, resource_name=None):
    label_arg = ''
    namespace_arg = ''
    resource_name_arg = ''
    resources = []

    if resource_name:
        resource_name_arg = f'{resource_name} '

    if namespace:
        namespace_arg = f'-n {namespace} '

    if label_selectors:
        label_format = '{key}{operator}{value}'
        label_parameters = ",".join(map(lambda selector: label_format.format_map(selector), label_selectors))
        label_arg = f'-l {label_parameters} '

    stdout = execute(f'kubectl get {resource_type} {resource_name_arg}{namespace_arg}{label_arg}-o yaml', ['NotFound'])

    if stdout:
        resource_data = yaml.load(stdout)
        resources = resource_data.get('items', [resource_data])

    return resources

