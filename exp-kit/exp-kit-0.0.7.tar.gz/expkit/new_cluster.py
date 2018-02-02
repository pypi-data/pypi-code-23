# coding: utf-8
from datetime import datetime
from datetime import timedelta
import time
import tempfile
import itertools
import copy

import boto3
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError
from pymongo import MongoClient
import paramiko
from halo import Halo
import click

from . import utils


def get_request_config(cluster_config):
    base = {
        'SpotPrice': '{}'.format(cluster_config['spot_price']),
        'TargetCapacity': cluster_config['size'],
        'TerminateInstancesWithExpiration': True,
        'ValidFrom': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
        'ValidUntil': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=365),
        'IamFleetRole': cluster_config['iam_fleet_role'],
        'LaunchSpecifications': [{
            'ImageId': cluster_config['image_id'],
            'KeyName': cluster_config['key_name'],
            'InstanceType': cluster_config['instance_type'],
            'BlockDeviceMappings': [{
                'VirtualName': 'Root',
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'VolumeSize': cluster_config['disk_size'],
                    'SnapshotId': cluster_config['snapshot_id'],
                    'VolumeType': 'gp2',
                    'DeleteOnTermination': True
                }
            }],
            'Monitoring': {
                'Enabled': False
            },
            'Placement': {
                'AvailabilityZone': 'us-west-1a',
            },
        }],
        'AllocationStrategy': 'lowestPrice',
        'Type': 'request'
    }
    return diversify_instance_type(base, cluster_config)

def diversify_instance_type(req_config, cluster_config):
    if type(cluster_config['instance_type']) is str:
        return req_config
    elif type(cluster_config['instance_type']) is list:
        spec = req_config['LaunchSpecifications'][0]
        req_config['AllocationStrategy'] = 'diversified'
        req_config['LaunchSpecifications'] = []
        for type_ in cluster_config['instance_type']:
            spec_template = copy.deepcopy(spec)
            spec_template['InstanceType'] = type_
            req_config['LaunchSpecifications'].append(spec_template)
        return req_config
    else:
        utils.error('Unrecognized instance_type field: {}'.format(cluster_config['instance_type']))

def send_request(client, config):
    """
    Create a new spot fleet request and send it.

    :return: request id
    :rtype: str
    """
    # Note: We cannot set SecurityGroup here in that it will cause an error.
    try:
        res = client.request_spot_fleet(SpotFleetRequestConfig=config)
    except (BotoCoreError, ClientError) as e:
        utils.error('{}'.format(e))
    utils.info('Spot fleet request {} created.'.format(res['SpotFleetRequestId']))
    return res['SpotFleetRequestId']

def wait_active(client, request_id, config):
    """
    Wait for spot fleet request with `request_id` to be active.

    :return: id of instances
    :rtype: list
    """
    def check_active():
        res = client.describe_spot_fleet_instances(SpotFleetRequestId=request_id)
        return len(res['ActiveInstances']) == config['TargetCapacity']
    utils.wait(10, 'Waiting for instances to be active.',
               120, '(Waiting too long, please go check AWS console.)',
               check_active)
    res = client.describe_spot_fleet_instances(SpotFleetRequestId=request_id)
    instance_id_list = [ i['InstanceId'] for i in res['ActiveInstances'] ]
    return instance_id_list

def wait_initialized(client, instance_id_list):
    """
    Wait for all instances specified by `instance_id_list` to be initialized.
    """
    def check_initialized():
        res = client.describe_instance_status(InstanceIds=instance_id_list)
        if len(res['InstanceStatuses']) <= 0:
            return False
        if not all([ s['InstanceStatus']['Status'] == 'ok' for s in res['InstanceStatuses'] ]):
            return False
        return True
    utils.wait(10, 'Waiting for instances to be initialized.',
               300, '(Waiting too long, please go check AWS console.)',
               check_initialized)

@Halo(text='Setting the security group of instances.', spinner='dots')
def set_security_group(client, instance_id_list, group_id):
    """
    Set the security group for instances specified by `instance_id_list`.
    """
    for instance_id in instance_id_list:
        client.modify_instance_attribute(InstanceId=instance_id, Groups=[ group_id ])


def get_host_line(ip):
    """
    Generate a line in the /etc/host.

    :rtype: str
    """
    return f'{ip} ip-{ip.replace(".", "-")}\n'

@Halo(text='Configuring hosts and SSH on each node.', spinner='dots')
def setup_communication(client, instance_id_list, user_name):
    """
    Setup communication prerequisite for executing program in parallel. It includes
    modify /etc/hosts, generate public keys, set authorized_keys, add known_hosts etc.
    """
    ec2 = boto3.resource('ec2')
    remote_home = '/home/{}'.format(user_name)
    instances = [ ec2.Instance(i) for i in instance_id_list ]
    temp_hosts = tempfile.NamedTemporaryFile()
    hosts = '127.0.0.1 localhost\n' + ''.join([ get_host_line(i.public_ip_address) for i in instances ])
    temp_hosts.file.write(hosts.encode('utf-8'))
    temp_hosts.file.flush()
    temp_machinefile = tempfile.NamedTemporaryFile()
    machinefile = ''.join([ (i.public_ip_address + '\n') for i in instances[1:] ])  # skip master node
    temp_machinefile.file.write(machinefile.encode('utf-8'))
    temp_machinefile.file.flush()
    keys = utils.get_user_config()['public_keys']
    for ssh, sftp in [ utils.get_session(i.public_ip_address, user_name) for i in instances ]:
        # appending temp_hosts to /etc/hosts
        sftp.put(temp_hosts.name, '/tmp/hosts.tmp')
        utils.check_command(ssh, 'sudo bash -c "cat /tmp/hosts.tmp > /etc/hosts"')
        # uploading temp_machinefile to ~/machinefile
        sftp.put(temp_machinefile.name, '{}/machinefile'.format(remote_home))
        # generate a new public key
        utils.check_command(ssh,
            'rm {}/.ssh/id_rsa ; '.format(remote_home) +  # don't use && in case it doesn't exist
            'ssh-keygen -q -t rsa -f {}/.ssh/id_rsa -N ""'.format(remote_home)
        )
        # collect public key
        stdin, stdout, stderr = ssh.exec_command('cat {}/.ssh/id_rsa.pub'.format(remote_home))
        keys.append(stdout.read().decode('utf-8').strip())
    temp_hosts.close()

    temp_keys = tempfile.NamedTemporaryFile()
    temp_keys.file.write(''.join(map(lambda s: s + '\n', keys)).encode('utf-8'))
    temp_keys.file.flush()
    for ssh, sftp in [ utils.get_session(i.public_ip_address, user_name) for i in instances ]:
        # appending temp_keys to ~/.ssh/authorized_keys
        sftp.put(temp_keys.name, '/tmp/keys.tmp')
        utils.check_command(ssh,
            'cat /tmp/keys.tmp > {}/.ssh/authorized_keys && '.format(remote_home) +
            'chmod 600 {}/.ssh/authorized_keys && '.format(remote_home) +
            'mv /tmp/keys.tmp {}/.ssh/known_hosts'.format(remote_home)
        )
    temp_keys.close()

def new(cluster_config):
    client = boto3.client('ec2')
    cluster_name = cluster_config['name']
    req_config = get_request_config(cluster_config)
    request_id = send_request(client, req_config)
    instance_id_list = wait_active(client, request_id, req_config)
    wait_initialized(client, instance_id_list)
    set_security_group(client, instance_id_list, cluster_config['security_group_id'])
    setup_communication(client, instance_id_list, cluster_config['user_name'])
    utils.store_cluster(cluster_name, request_id, instance_id_list)
    utils.info('Cluster {} created. Master IP is {}.'.format(click.style(cluster_name, bold=True), utils.get_master_ip(cluster_name)))
