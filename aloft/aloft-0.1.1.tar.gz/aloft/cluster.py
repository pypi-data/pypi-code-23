import contextlib
import os
import time
import yaml
from aloft import aws
from aloft import cluster_config
from aloft import host
from aloft import chart_config
from aloft import output
from aloft.process import execute
from aloft.vpc import delete_vpc, get_or_create_vpc
from subprocess import CalledProcessError


def get_and_print_current_cluster(output_type):
    current_cluster_id = get_current_cluster_id()
    cluster = get_cluster_by_cluster_id(current_cluster_id)
    print_clusters([cluster], output_type)


def get_current_cluster_id():
    stdout = execute('kubectl config current-context', quiet=True)
    return stdout.rstrip()


def get_and_print_clusters(cluster_domain, output_type):
    clusters = get_clusters(cluster_domain)
    print_clusters(clusters, output_type)


def print_clusters(clusters, output_type):
    if output_type == 'yaml':
        output.print_list_as_yaml(clusters)
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

    output.print_table(['NAME', 'VERSION', 'CIDR'], rows, '{0: <40} {1: <10} {2: <18}')


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
    assume_role_by_vpc_id(vpc_id)
    state_store_locator = get_state_store_locator(vpc_id)
    stdout = execute(f'kops get clusters -o yaml --state {state_store_locator}', ['no clusters found'], quiet=True)
    clusters = []

    if stdout:
        for cluster_definition in stdout.split('---'):
            cluster = yaml.load(cluster_definition)
            clusters.append(cluster)

    return clusters


def use_cluster_for_release(release_id, chart_set, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    cluster_id = release_config['cluster']
    use_cluster(cluster_id)


def use_cluster(cluster_id):
    assume_role_by_cluster_id(cluster_id)
    state_store_locator = get_state_store_locator_by_cluster_id(cluster_id)
    execute(f'kops export kubecfg {cluster_id} --state {state_store_locator}')


def delete_cluster(cluster_id):
    assume_role_by_cluster_id(cluster_id)
    state_store_locator = get_state_store_locator_by_cluster_id(cluster_id)
    execute(f'kops delete cluster {cluster_id} --yes --state {state_store_locator}')


def get_state_store_locator_by_cluster_id(cluster_id):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    return get_state_store_locator(vpc_id)


def get_state_store_locator(vpc_id):
    state_store_name = get_state_store_name(vpc_id)
    return f's3://{state_store_name}'


def get_state_store_name(vpc_id):
    return f'k8s-state.{vpc_id}'


def assume_role_by_cluster_id(cluster_id):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    assume_role_by_vpc_id(vpc_id)


def get_aws_profile_name_by_cluster_id(cluster_id):
    return get_vpc_name_by_custer_id(cluster_id)


def assume_role_by_vpc_id(vpc_id):
    aws_profile_name = get_aws_profile_name_by_vpc_id(vpc_id)
    aws.assume_role(aws_profile_name)


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
    domain_cluster_config_directory = get_domain_cluster_values_directory(domain)
    vpc_names = os.listdir(domain_cluster_config_directory)

    if len(vpc_names) == 0:
        raise ValueError(f'No cluster configuration found in {domain_cluster_config_directory}.')

    vpc_names.sort()

    return vpc_names


def get_domain(cluster_id):
    return cluster_id.split('.')[-2:]


def get_domain_cluster_values_directory(domain):
    base_cluster_config_directory = cluster_config.get_cluster_values_directory()
    return f'{base_cluster_config_directory}/{domain}'


def get_default_domain_from_cluster_config():
    base_cluster_config_directory = cluster_config.get_cluster_values_directory()
    domains = os.listdir(base_cluster_config_directory)

    if len(domains) > 1:
        raise ValueError(f'More than one domain config directory found in {base_cluster_config_directory}. You must '
                         f'specify a <domain>')
    elif not domains:
        raise ValueError(f'No cluster domain configurations found in {base_cluster_config_directory}.')

    return domains[0]


def conditionally_create_vpc_and_cluster(cluster_id):
    vpc = get_or_create_vpc_by_cluster_id(cluster_id)
    create_cluster_and_attach_network(cluster_id, vpc)


def create_cluster_and_attach_network(cluster_id, vpc):
    vpn_name = get_vpc_name_by_custer_id(cluster_id)
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    state_store_name = get_state_store_name(vpc_id)

    aws.conditionally_create_hosted_zone_and_setup_ns_records(cluster_id, vpc_id)
    host.wait_for_domain_to_resolve(cluster_id)
    aws.get_or_create_s3_bucket(state_store_name)
    create_cluster(cluster_id, vpc)
    propagate_cluster_route_tables(cluster_id, vpn_name)
    add_cluster_node_policies(cluster_id)
    wait_for_cluster_to_be_ready(cluster_id)
    initialize_helm()


def propagate_cluster_route_tables(cluster_id, vpn_name):
    vpn_gateway_id = aws.get_vpn_gateway_id(vpn_name)
    route_table_ids = aws.get_route_table_ids(cluster_id)

    for route_table_id in route_table_ids:
        aws.propagate_route_table(route_table_id, vpn_gateway_id)


def add_cluster_node_policies(cluster_id):
    node_policies_filename = cluster_config.get_node_policies_filename()

    with open(node_policies_filename, 'r') as stream:
        node_policies = stream.read()
        aws.set_role_policy(f'nodes.{cluster_id}', 'systemPolicy', node_policies)


def wait_for_cluster_to_be_ready(cluster_id):
    output.print_action(f'Waiting for {cluster_id} to be ready.')
    time.sleep(300)

    while not validate_cluster(cluster_id):
        time.sleep(20)


def validate_cluster(cluster_id):
    state_store_locator = get_state_store_locator_by_cluster_id(cluster_id)
    valid = False

    try:
        execute(f'kops validate cluster {cluster_id} --state {state_store_locator}')
        valid = True
    except CalledProcessError:
        pass

    return valid


def create_cluster(cluster_id, vpc):
    output.print_action(f'Creating cluster {cluster_id} in {vpc["Name"]} vpc.')
    state_store_locator = get_state_store_locator_by_cluster_id(cluster_id)
    generated_cluster_config_filename = cluster_config.generated_cluster_config_filename(cluster_id)
    generate_cluster_config_from_template(cluster_id, vpc, generated_cluster_config_filename)

    execute(f'kops create -f {generated_cluster_config_filename} --state {state_store_locator}')
    create_ssh_secret(cluster_id, state_store_locator)
    execute(f'kops update cluster {cluster_id} --yes --state {state_store_locator}')


def generate_cluster_config_from_template(cluster_id, vpc, generated_cluster_config_filename):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    cluster_template_filename = cluster_config.get_cluster_template_filename()
    default_cluster_values_filename = cluster_config.get_default_cluster_values_filename()
    cluster_values_filename = cluster_config.get_cluster_values_filename(cluster_id)
    vpc_values_filename = cluster_config.get_vpc_config_filename(vpc_id)
    dynamic_values_filename = cluster_config.get_create_dynamic_values_filename(cluster_id)

    create_dynamic_values_file(dynamic_values_filename, vpc, cluster_id)

    execute(f'kops toolbox template '
            f'--values {default_cluster_values_filename} '
            f'--values {cluster_values_filename} '
            f'--values {vpc_values_filename} '
            f'--values {dynamic_values_filename} '
            f'--template {cluster_template_filename} '
            f'--format-yaml=true > {generated_cluster_config_filename}')


def create_dynamic_values_file(vpc_id_value_filename, vpc, cluster_id):
    output.write_to_file(
        vpc_id_value_filename,
        f'networkId: {vpc["VpcId"]}\n'
        f'clusterFQDN: {cluster_id}\n'
        f'kopsStateStore: {get_state_store_locator_by_cluster_id(cluster_id)}\n'
    )


def create_ssh_secret(cluster_id, state_store_locator):
    key_filename = '/tmp/cluster_rsa'
    create_cluster_ssh_keys(key_filename)
    execute(f'kops create secret --name {cluster_id} sshpublickey admin'
            f' -i "{key_filename}.pub" --state {state_store_locator}')
    remove_cluster_ssh_keys(key_filename)


def initialize_helm():
    execute('helm init')
    execute('kubectl rollout status -w deployment/tiller-deploy --namespace=kube-system')


def create_cluster_ssh_keys(key_filename):
    remove_cluster_ssh_keys(key_filename)
    execute(f'ssh-keygen -q -f {key_filename} -t rsa -N ""')


def remove_cluster_ssh_keys(key_filename):
    remove(key_filename)
    remove(f'{key_filename}.pub')


def remove(filename):
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)


def get_or_create_vpc_by_cluster_id(cluster_id):
    vpc_id = get_vpc_id_by_cluster_id(cluster_id)
    return get_or_create_vpc(vpc_id)


def delete_vpc_if_no_clusters_exist(vpc_id):
    clusters = get_clusters_by_vpc_id(vpc_id)

    if len(clusters) > 0:
        output.print_action(f'Not deleting VPC. All clusters must be deleted before deleting the VPC.')
        print_cluster_names(clusters)
        print()
    else:
        delete_vpc(vpc_id)
