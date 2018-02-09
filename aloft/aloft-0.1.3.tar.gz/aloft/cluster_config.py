import yaml
from io import open
from aloft import config


def get_cluster_config_values(cluster_id):
    cluster_config_filename = get_cluster_values_filename(cluster_id)
    with open(cluster_config_filename, 'r') as stream:
        return yaml.load(stream)


def get_cluster_values_filename(cluster_id):
    cluster_config_directory = get_cluster_values_directory()
    cluster_name, vpc_name, domain_name = split_cluster_id(cluster_id)
    return f'{cluster_config_directory}/{domain_name}/{vpc_name}/{cluster_name}/cluster.yaml'


def get_default_cluster_values_filename():
    cluster_template_directory = get_cluster_template_directory()
    return f'{cluster_template_directory}/values.yaml'


def get_vpc_config_filename(vpc_id):
    cluster_config_directory = get_cluster_values_directory()
    vpc_name, domain_name = split_vpc_id(vpc_id)
    return f'{cluster_config_directory}/{domain_name}/{vpc_name}/vpc.yaml'


def get_create_dynamic_values_filename(cluster_id):
    return f'/tmp/{cluster_id}-dynamic.yaml'


def generated_cluster_config_filename(cluster_id):
    return f'/tmp/{cluster_id}.yaml'


def get_cluster_template_filename():
    cluster_template_directory = get_cluster_template_directory()
    return f'{cluster_template_directory}/template.yaml'


def get_node_policies_filename():
    cluster_template_directory = get_cluster_template_directory()
    return f'{cluster_template_directory}/node-policies.json'


def split_cluster_id(cluster_id):
    parts = cluster_id.split('.')
    cluster_name = parts[0]
    vpc_name = parts[1]
    domain_name = '.'.join(parts[2:4])
    return cluster_name, vpc_name, domain_name


def split_vpc_id(vpc_id):
    parts = vpc_id.split('.')
    vpc_name = parts[0]
    domain_name = '.'.join(parts[1:3])
    return vpc_name, domain_name


def get_cluster_template_directory():
    base_chart_config_directory = get_base_cluster_config_directory()
    return f'{base_chart_config_directory}/template'


def get_cluster_values_directory():
    base_chart_config_directory = get_base_cluster_config_directory()
    return f'{base_chart_config_directory}/values'


def get_base_cluster_config_directory():
    aloft_config_directory = config.get_aloft_config_directory()
    return f'{aloft_config_directory}/clusters'
