from aloft import aws
from aloft import input
from aloft import cluster_config


def get_or_create_vpc(vpc_id):
    vpc_name = get_vpc_name_by_vpc_id(vpc_id)
    vpc = get_vpc(vpc_name)

    if not vpc:
        vpc = create_vpc(vpc_id)

    return vpc


def get_vpc(vpc_name):
    return aws.get_vpc_by_name(vpc_name)


def create_vpc(vpc_id):
    vpc_name = get_vpc_name_by_vpc_id(vpc_id)
    vpc_values_filename = cluster_config.get_vpc_config_filename(vpc_id)
    vpc_config = input.read_yaml_file(vpc_values_filename)

    vpc = aws.create_vpc(vpc_name, vpc_config['networkCIDR'])
    aws.create_and_attach_internet_gateway(vpc)
    aws.create_and_attach_vpn_gateway(vpc)
    return vpc


def delete_vpc(vpc_id):
    vpc_name = get_vpc_name_by_vpc_id(vpc_id)
    aws.delete_network_and_vpc(vpc_name)


def get_vpc_config(vpc_id):
    vpc_values_filename = cluster_config.get_vpc_config_filename(vpc_id)
    return input.read_yaml_file(vpc_values_filename)


def get_vpc_name_by_vpc_id(vpc_id):
    return vpc_id.split('.', 1)[0]

