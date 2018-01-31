import os
import yaml
from aloft.aws import set_aws_profile
from aloft.input import get_directory_from_environment
from aloft.output import print_table, print_list_as_yaml
from aloft.process import execute


def get_and_print_current_cluster(output_type):
    current_cluster_id = get_current_cluster_id()
    cluster = get_cluster_by_cluster_id(current_cluster_id)
    print_clusters([cluster], output_type)


def get_current_cluster_id():
    output = execute('kubectl config current-context', quiet=True)
    return output.rstrip()


def get_and_print_clusters(cluster_domain, output_type):
    clusters = get_clusters(cluster_domain)
    print_clusters(clusters, output_type)


def print_clusters(clusters, output_type):
    if output_type == 'yaml':
        print_list_as_yaml(clusters)
    elif output_type == 'name':
        print_cluster_names(clusters)
    else:
        print_cluster_text(clusters)


def print_cluster_names(clusters):
    for cluster in clusters:
        print(cluster['metadata']['name'])


def print_cluster_text(clusters):
    rows = []

    for cluster in clusters:
        rows.append([
            cluster['metadata']['name'],
            cluster['spec']['kubernetesVersion'],
            cluster['spec']['networkCIDR'],
        ])

    print_table(['NAME', 'VERSION', 'CIDR'], rows, '{0: <40} {1: <10} {2: <18}')


def get_cluster_by_cluster_id(cluster_id):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    clusters = get_clusters_by_vpc_id(vpc_id)
    matching_clusters = list(filter(lambda cluster: cluster['metadata']['name'] == cluster_id, clusters))

    if len(matching_clusters) != 1:
        raise KeyError(f'Unable to get cluster data for: {cluster_id}')

    return matching_clusters[0]


def get_clusters(cluster_domain):
    vpc_names = get_vpc_names(cluster_domain)
    clusters = []

    for vpc_name in vpc_names:
        vpc_id = get_vpc_id_by_vpc_name_and_cluster_domain(vpc_name, cluster_domain)
        clusters += get_clusters_by_vpc_id(vpc_id)

    return clusters


def get_clusters_by_vpc_id(vpc_id):
    set_aws_profile_by_vpc_id(vpc_id)
    state_store_locator = get_state_store_locator(vpc_id)
    output = execute(f'kops get clusters -o yaml --state {state_store_locator}', ['no clusters found'], quiet=True)
    clusters = []

    if output:
        for cluster_definition in output.split('---'):
            cluster = yaml.load(cluster_definition)
            clusters.append(cluster)

    return clusters


def     create_cluster(cluster_id):
    print(f'created cluster {cluster_id}')


def use_cluster(cluster_id):
    set_aws_profile_by_cluster_id(cluster_id)
    state_store_locator = get_state_store_locator_by_cluster_id(cluster_id)
    execute(f'kops export kubecfg {cluster_id} --state {state_store_locator}')


def delete_cluster(cluster_id):
    set_aws_profile_by_cluster_id(cluster_id)
    state_store_locator = get_state_store_locator_by_cluster_id(cluster_id)
    execute(f'kops delete cluster {cluster_id} --yes --state {state_store_locator}')


def create_namespace(namespace):
    execute(f'kubectl create namespace {namespace}', ['AlreadyExists'])


def delete_namespace(namespace):
    execute(f'kubectl delete namespace {namespace}', ['NotFound'])


def get_state_store_locator_by_cluster_id(cluster_id):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    return get_state_store_locator(vpc_id)


def get_state_store_locator(vpc_id):
    return f's3://k8s-state.{vpc_id}'


def set_aws_profile_by_cluster_id(cluster_id):
    aws_profile_name = get_aws_profile_name_by_cluster_id(cluster_id)
    set_aws_profile(aws_profile_name)


def get_aws_profile_name_by_cluster_id(cluster_id):
    return get_vpc_name_by_custer_id(cluster_id)


def set_aws_profile_by_vpc_id(vpc_id):
    aws_profile_name = get_aws_profile_name_by_vpc_id(vpc_id)
    set_aws_profile(aws_profile_name)


def get_aws_profile_name_by_vpc_id(vpc_id):
    return get_vpc_name_by_vpc_id(vpc_id)


def get_vpc_id_by_vpc_name_and_cluster_domain(vpc_name, cluster_domain):
    return f'{vpc_name}.{cluster_domain}'


def get_vpc_name_by_custer_id(cluster_id):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    return get_vpc_name_by_vpc_id(vpc_id)


def get_vpc_name_by_vpc_id(vpc_id):
    return vpc_id.split('.', 1)[0]


def get_vpc_id_by_cluster_id(cluster_id):
    return cluster_id.split('.', 1)[1]


def get_vpc_names(domain):
    domain_cluster_config_directory = get_domain_cluster_config_directory(domain)
    vpc_names = os.listdir(domain_cluster_config_directory)

    if len(vpc_names) == 0:
        raise ValueError(f'No cluster configuration found in {domain_cluster_config_directory}.')

    vpc_names.sort()

    return vpc_names


def get_domain(cluster_id):
    return cluster_id.split('.')[-2:]


def get_base_cluster_config_directory():
    return get_directory_from_environment('K8S_CLUSTER_CONFIG') + '/config'


def get_domain_cluster_config_directory(domain):
    base_cluster_config_directory = get_base_cluster_config_directory()
    return f'{base_cluster_config_directory}/{domain}'


def get_default_domain_from_cluster_config():
    base_cluster_config_directory = get_base_cluster_config_directory()
    domains = os.listdir(base_cluster_config_directory)

    if len(domains) > 1:
        raise ValueError(f'More than one domain config directory found in {base_cluster_config_directory}. You must '
                         f'specify a <domain>')
    elif not domains:
        raise ValueError(f'No cluster domain configurations found in {base_cluster_config_directory}.')

    return domains[0]
