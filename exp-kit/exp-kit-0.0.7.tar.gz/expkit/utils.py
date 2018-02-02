# coding: utf-8
import logging
import sys
import itertools
import time
from functools import lru_cache
import json
import difflib
import contextlib

import click
import boto3
import paramiko
from pymongo import MongoClient
from halo import Halo


# configure logging options
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('paramiko').setLevel(logging.WARN)

env = {
    'user_config': {
        'mongo_host': 'localhost',
        'mongo_port': 27017,
        'bare_output': False
    },
    'collection': None
}

def error(content):
    click.echo(click.style('ERROR! ', bold=True, fg='red'), nl=False)
    click.echo(content)
    sys.exit(1)

def warn(content):
    click.echo(click.style('WARN! ', bold=True, fg='yellow'), nl=False)
    click.echo(content)

def info(content):
    click.echo(click.style('INFO ', bold=True, fg='green'), nl=False)
    click.echo(content)

def load_user_config(path):
    env['user_config'].update(parse_json_file(path))
    for key in [ 'key_path', 'key_name', 'iam_fleet_role', 'public_keys' ]:
        if key not in env['user_config']:
            error('Missing {} in user configuration.'.format(key))
    mongo_host = env['user_config']['mongo_host']
    mongo_port = env['user_config']['mongo_port']
    client = MongoClient(mongo_host, mongo_port)
    try:
        with halo_wrapper(text='Connecting to MongoDB ...', spinner='dots'):
            client.admin.command('ismaster')
    except:
        error('Cannot connect to MongoDB.')
    env['collection'] = client['aws']['clusters']

def get_user_config():
    return env['user_config']

def parse_json_file(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        error('{} not exists.'.format(click.format_filename(path)))
    except json.decoder.JSONDecodeError as e:
        error('Parsing json file {} failed. {}'.format(click.format_filename(path), e))

def load_cluster_instances(cluster_name):
    try:
        instance_id_list = env['collection'].find({ 'name': cluster_name }).next()['instance_id_list']
        ec2 = boto3.resource('ec2')
        return [ ec2.Instance(i) for i in instance_id_list ]
    except StopIteration:
        error('No cluster with name {} found.'.format(click.style(cluster_name, bold=True)))

def get_master_ip(cluster_name):
    instances = load_cluster_instances(cluster_name)
    return instances[0].public_ip_address

def check_command(ssh_client, command, debug=False):
    _, stdout, stderr = ssh_client.exec_command(command)
    stdout.channel.set_combine_stderr(True)
    is_success = stdout.channel.recv_exit_status() == 0
    if debug or (not is_success):
        for line in stdout.xreadlines():
            print(line, end='', flush=True)
    return is_success

def wait(interval, prompt, timeout, timeout_prompt, check_callback):
    spinner = Halo(text=prompt, spinner='dots').start()
    waited = 0
    while True:
        if check_callback():
            spinner.stop()
            return
        time.sleep(interval)
        waited += interval
        if waited >= timeout:
            spinner.start('{} {}'.format(prompt, timeout_prompt))

@lru_cache(maxsize=128)
def get_session(ip, username):
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    ssh.connect(ip, username=username, key_filename=env['user_config']['key_path'])
    sftp = ssh.open_sftp()
    return ssh, sftp

def store_cluster(cluster_name, request_id, instance_id_list):
    env['collection'].update(
        { 'name': cluster_name },
        { 'name': cluster_name, 'request_id': request_id, 'instance_id_list': instance_id_list },
        upsert=True
    )

def match_cluster_name(cluster_name):
    try:
        env['collection'].find({ 'name': cluster_name }).next()
        return cluster_name
    except StopIteration:
        candidates = [ doc['name'] for doc in env['collection'].find() ]
        matches = difflib.get_close_matches(cluster_name, candidates)
        styled_name = click.style(cluster_name, bold=True)
        if len(matches) == 0:
            error('Cannot find cluster with name {}.'.format(styled_name))
        else:
            if click.confirm('No cluster with name {} found. Do you mean {}?'.format(
                styled_name, click.style(matches[0], bold=True)
            )):
                return matches[0]
            else:
                error('Please double-check the cluster name.')

def get_request_id(cluster_name):
    try:
        doc = env['collection'].find({ 'name': cluster_name }).next()
        return doc['request_id']
    except StopIteration:
        error('Internal error: get_request_id failed.\n'
              'Please report to https://github.com/All-less/aws-experiment-kit/issues. '
              'Sorry for any inconvenience!')

def delete_cluster_information(cluster_name):
    env['collection'].remove({ 'name': cluster_name })

def load_all_clusters():
    return list(env['collection'].find())

def halo_wrapper(**kwargs):
    return null_context() if env['user_config']['bare_output'] else Halo(**kwargs)

@contextlib.contextmanager
def null_context():
    yield
