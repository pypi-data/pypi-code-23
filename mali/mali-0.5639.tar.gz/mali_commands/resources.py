# -*- coding: utf8 -*-
import base64
import logging
import os
import requests

import click
import requests
import six

from .commons import output_result


def get_home_path():
    if six.PY2:
        from os.path import expanduser, join
        home = expanduser("~")
    else:
        from pathlib import Path
        home = str(Path.home())
    return home


def get_ssh_path():
    from os.path import join
    return join(get_home_path(), '.ssh', 'id_rsa')


def make_data_dir(data_dir_path):
    if six.PY2:
        import errno
        try:
            os.makedirs(data_dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    else:
        os.makedirs(data_dir_path, exist_ok=True)


def try_import_docker_and_crypto():
    try:
        import docker
        import cryptography
        return docker, cryptography
    except ImportError as ex:
        raise click.BadOptionUsage('Docker deps are missing. Please run pip install mali[docker], %s' % (ex))


def load_ssh_key(ssh_key_path):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    with open(ssh_key_path, 'rb') as f:
        ssh_key_data = f.read()
    private_key = serialization.load_pem_private_key(ssh_key_data, password=None, backend=default_backend())
    key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
    logging.info('ssh key loaded from %s', ssh_key_path)
    return key_bytes


DOCKER_IMAGE = 'docker:latest'


def pull_image_from_image(client, image):
    import docker
    ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}

    try:
        client.images.get(DOCKER_IMAGE)
    except docker.errors.NotFound:
        print('Pulling docker image')
        client.images.pull(DOCKER_IMAGE)
    cmd = 'docker pull {}'.format(image)
    cont = client.containers.run(DOCKER_IMAGE, command=cmd, auto_remove=True, volumes=ADMIN_VOLUME, environment={'ML_RM_MANAGER': '1'}, detach=True)
    logger_hanler = cont.logs(stdout=True, stderr=True, stream=True)
    for log in logger_hanler:
        logging.info(log)
    return client.images.get(image)


def auth_resource(ctx, org):
    import requests
    result = ctx.obj.handle_api(ctx.obj, requests.get, '{org}/resource/authorise'.format(org=org))
    return result.get('token')


def validate_and_get_docker_client():
    import docker
    import requests
    client = docker.from_env()
    try:
        client.ping()
    except docker.errors.DockerException as ex:
        raise click.BadArgumentUsage('Failed to connect to docker host %s' % (str(ex)))
    except requests.exceptions.ConnectionError as ex:
        raise click.BadArgumentUsage('Failed to connect to docker host %s' % (str(ex)))
    logging.info('Docker host verified')
    return client


def pull_ml_image(config, docker_client):
    print('Getting/updating MissingLinks Resource Manager image')
    img = pull_image_from_image(docker_client, config.rm_manager_image)
    return img


def _get_combined_volume_path(*args):
    res = {}
    for a in args:
        res.update(a)
    return res


def _docker_present(command, *args, **kwargs):
    import docker
    try:
        return command(*args, **kwargs) or True  # we are looking only for exceptions here
    except docker.errors.NotFound:
        return False


def _pad_str_to_len(s, pad_len=32):
    return s + (pad_len - len(s) % pad_len) * ' '


def b64_encode_to_utf8(s):
    if six.PY3 and not isinstance(s, bytes):
        s = s.encode('utf-8')
    return base64.b64encode(s).decode('utf-8')


def b64_decode_from_utf8(s):
    if six.PY3 and not isinstance(s, bytes):
        s = s.encode('utf-8')
    return base64.b64decode(s)


def get_boto_client(client_type, region_name=None):
    import boto3
    my_session = boto3.session.Session()
    return boto3.client(client_type, region_name=region_name or my_session.region_name)


def encrypt_strint_with_boto_kms(input_str, arn):
    from Crypto.Cipher import AES
    kms_client = get_boto_client('kms')

    data_key = kms_client.generate_data_key(KeyId=arn, KeySpec='AES_256')
    ciphertext_blob = data_key.get('CiphertextBlob')
    plaintext_key = data_key.get('Plaintext')
    iv = kms_client.generate_random(NumberOfBytes=16)['Plaintext']
    encryption_suite = AES.new(plaintext_key, AES.MODE_CBC, iv)
    cipher_text = encryption_suite.encrypt(_pad_str_to_len(input_str))
    return dict(iv=b64_encode_to_utf8(iv), key=b64_encode_to_utf8(ciphertext_blob), data=b64_encode_to_utf8(cipher_text))


def decrypt_string_with_boto_kms(input_data, region):
    from Crypto.Cipher import AES

    iv, key, data = [b64_decode_from_utf8(x) for x in input_data]

    kms_client = get_boto_client('kms', region_name=region)

    decrypted_key = kms_client.decrypt(CiphertextBlob=key).get('Plaintext')
    cypher = AES.new(decrypted_key, AES.MODE_CBC, iv)
    return cypher.decrypt(data).decode('utf-8').rstrip()


def validate_running_resource_manager(config, docker_client, force):
    currnet_rm = _docker_present(docker_client.containers.get, config.rm_container_name)
    if not currnet_rm:
        return

    if not force:
        raise click.BadOptionUsage('Can not install resource manger while one is running. run `docker kill {}` do stop and reuse config or re-run with `--force` flag to clear all configuration'.format(currnet_rm.name))

    print('Killing current Resource Manger (%s) due to --force flag' % currnet_rm.id)
    currnet_rm.kill()


def get_config_prefix_and_file(config):
    with open(config.config.config_file_abs_path, 'rb') as f:
        config_data = f.read()
    config_data = b64_encode_to_utf8(config_data)
    prefix = None
    if config.config.config_prefix is not None:
        prefix = config.config.config_prefix
    return prefix, config_data


ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}


def _apply_config_to_volume(config, docker_client, ssh_key, token, prefix=None, config_data=None):
    if token is None and ssh_key is None:
        return

    config_volume = {config.rm_config_volume: {'bind': '/config'}}
    conf_mounts = _get_combined_volume_path(ADMIN_VOLUME, config_volume)

    ws_server = config.rm_socket_server

    if prefix is None and config_data is None:
        id_token = config.id_token
        if id_token is None:
            # TODO: make backend data commands support resource token
            raise click.BadOptionUsage('Please call mali auth init first')
        prefix, config_data = get_config_prefix_and_file(config)

    command = ['config', '--ml-server', ws_server, '--ml-config-file', config_data]
    if prefix is not None:
        command.extend(['--ml-config-prefix', prefix])
    if token is not None:
        command.append('--ml-token')
        command.append(token)

    if ssh_key is not None:
        command.append('--ssh-private-key')
        command.append(ssh_key)

    cont = docker_client.containers.run(config.rm_manager_image, command=command, volumes=conf_mounts, environment={'ML_RM_MANAGER': '1'}, detach=True)
    exit_code = cont.wait()
    if exit_code != 0:
        print(cont.logs())
    cont.remove()


def _handle_token_and_data_path(ctx, force, org, token=None):
    cur_config = ctx.obj.config.resource_manager_config
    if force:
        print('Current host config is deleted due to `--force` flag')
        cur_config = {}

    new_token = token or cur_config.get('token')

    if new_token is None:
        new_token = auth_resource(ctx, org)
    ctx.obj.config.update_and_save({
        'resource_manager': {
            'token': new_token,
        }
    })
    return new_token


def _validate_apply_config(ctx, docker_client, org, force, ssh_key_path, token):
    config = ctx.obj
    config_volume_name = config.rm_config_volume

    if force and _docker_present(docker_client.volumes.get, config_volume_name):
        print('Deleting config volume (%s) due to --force flag')
        docker_client.volumes.get(config_volume_name).remove(force=True)

    new_image = not _docker_present(docker_client.volumes.get, config_volume_name)

    ssh_key = None
    if new_image:
        docker_client.volumes.create(config_volume_name)
        if ssh_key_path is None:
            ssh_key_path = click.prompt(text='SSH key path (--ssh-key-path)', default=get_ssh_path())

    token = _handle_token_and_data_path(ctx, force, org, token=token)

    if ssh_key_path is not None:
        ssh_key = load_ssh_key(ssh_key_path)

    _apply_config_to_volume(config, docker_client, ssh_key, token)
    return


def _valiadte_config_volume(config, docker_client):
    if not _docker_present(docker_client.volumes.get, config.rm_config_volume):
        raise click.BadArgumentUsage('Configuration volume is missing. Please re-install')


def _run_resource_manager(config, docker_client):
    _valiadte_config_volume(config, docker_client)
    print('Starting Resource Manager')
    config_volume = {config.rm_config_volume: {'bind': '/config'}}
    run_mounts = _get_combined_volume_path(ADMIN_VOLUME, config_volume)
    return docker_client.containers.run(
        config.rm_manager_image,
        command=['run'],
        auto_remove=True,
        volumes=run_mounts,
        environment={'ML_RM_MANAGER': '1', 'ML_CONFIG_VOLUME': config.rm_config_volume},
        detach=True,
        network='host',
        name=config.rm_container_name)


def get_selected_fields(client_input, default_fields=None):
    display_fields = default_fields
    if client_input is not None:
        selected_fields = [x.strip() for x in client_input.split(',')]
        if len(selected_fields) == 1 and selected_fields[0] == '*':
            display_fields = None
        else:
            display_fields = selected_fields
    return display_fields


def append_optional_filters_to_url(url, **kwargs):
    filters = ['{}={}'.format(k, v) for k, v in kwargs.items() if v is not None]
    if len(filters) > 0:
        url = '{url}?{filters}'.format(url=url, filters='&'.join(filters))
    return url


@click.group('resources', help='Operations on resource managers')
def resource_commands():
    pass


class BotoWrapper(object):
    def __init__(self, session):
        import boto3
        self._boto3 = boto3
        self.session = session
        self._regions = None
        self._encryption_keys = None
        self._vpcs = None
        self._roles = None

    @property
    def regions(self):
        if self._regions is None:
            self._regions = self.session.get_available_regions('ec2')
        return self._regions

    @property
    def region(self):
        return self.session.region_name

    def _get_client(self, service):
        return self._boto3.client(service)

    def _get_resource(self, resource):
        return self._boto3.resource(resource)

    @property
    def encryption_keys(self):
        if self._encryption_keys is None:
            kms_client = self._get_client('kms')
            keys = kms_client.list_keys(Limit=1000).get('Keys')
            self._encryption_keys = [x['KeyArn'] for x in keys]
        return self._encryption_keys

    def set_region(self, region):
        self.session = self._boto3.session.Session(region_name=region)

    def create_encryption_key(self, name):
        kms_client = self._get_client('kms')
        self._encryption_keys = None
        arn = kms_client.create_key(
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS',
            Description='Used for encrypting various data by MissingLink',
            Tags=[
                {'TagKey': 'CreatedBy', 'TagValue': 'MissingLink AI'},
                {'TagKey': 'Name', 'TagValue': name},
            ]
        ).get('KeyMetadata', {}).get('Arn')
        kms_client.create_alias(AliasName='alias/%s' % name, TargetKeyId=arn)
        return arn

    @property
    def vpcs(self):
        if self._vpcs is None:
            def get_vpc(x):
                return x['VpcId'], x['CidrBlock']

            non_default_vpcs = self._get_client('ec2').describe_vpcs(Filters=[dict(Name='isDefault', Values=['false'])])
            default_vpcs = self._get_client('ec2').describe_vpcs(Filters=[dict(Name='isDefault', Values=['true'])])
            self._vpcs = [get_vpc(x) for x in non_default_vpcs['Vpcs']] + [get_vpc(x) for x in default_vpcs['Vpcs']]
        return self._vpcs


class AwsProfileHelper:
    def __init__(self, boto_wrapper):
        self.boto = boto_wrapper

    def region(self, region):
        while region is None or region not in self.boto.regions:
            region = click.prompt(text='Target AWS region', default=self.boto.region, type=click.Choice(self.boto.regions))
        if region != self.boto.region:
            print('Reconnecting to %s' % region)
            self.boto.set_region(region)
        return region

    def vpc(self, vpc):
        vpcs = ["LIST"] + [x[0] for x in self.boto.vpcs]
        def_vpc = vpcs[-1]
        while vpc is None or vpc not in [x[0] for x in self.boto.vpcs]:
            vpc = click.prompt(text='Target VPC', default=def_vpc, type=click.Choice(vpcs))
            if vpc == "LIST":
                print('List of available VPCs. The default VPC is listed last')
                print()
                for vpc in self.boto.vpcs:
                    print('%s | %s' % vpc)
                print()
                print('Creating of new VPCs in not supported. Please create one using AWS website or APIs')
                vpc = None
        return vpc


@click.group('resources', help='Experimental! Resource Management')
def resource_commands():
    pass


@resource_commands.command('state', help="Get the state of the local resource manager")
@click.pass_context
def get_state(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if cur_instance:
        print('%s: %s (%s)' % (cur_instance.name, cur_instance.status, cur_instance.short_id))
    else:
        _valiadte_config_volume(ctx.obj, docker_client)
        print('not running')


@resource_commands.command('start', help="Start resource manager")
@click.pass_context
def start_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if cur_instance:
        raise click.BadOptionUsage('Already running')

    _run_resource_manager(ctx.obj, docker_client)
    print('The resource manager is configured and running')


@resource_commands.command('watch', help="Start resource manager")
@click.pass_context
def watch_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if not cur_instance:
        cur_instance = _run_resource_manager(ctx.obj, docker_client)
    for line in cur_instance.logs(stream=True):
        line = line.strip()
        if not isinstance(line, six.string_types):
            line = line.decode('utf-8')
        print(line)


@resource_commands.command('stop', help="Stop running resource manager")
@click.pass_context
def stop_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if not cur_instance:
        raise click.BadOptionUsage('not running')

    print('Stopping ...')
    cur_instance.stop()
    print('Stopped')


@resource_commands.command('kill', help="Kill running resource manager")
@click.pass_context
def kill_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if not cur_instance:
        raise click.BadOptionUsage('not running')

    print('Killing ...')
    cur_instance.kill()
    print('Killed')


@resource_commands.command('list', help="Lists resource managers registered for your organization")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--connected/--disconnected', default=None, required=False, help='Show only connected / disconnected resource managers. by default lists both')
@click.option('--gpu/--cpu', default=None, required=False, help='Show only  resources with / without configured GPU. by default lists both')
@click.option('--fields', default=None, required=False, help='Fields to display, separated by comma, * for all fields')
def list_resources(ctx, org, connected, gpu, fields):
    from mali_commands.commons import output_result
    url = append_optional_filters_to_url('{org}/resources'.format(org=org), connected=connected, gpu=gpu)
    result = ctx.obj.handle_api(ctx.obj, requests.get, url)
    display_fields = get_selected_fields(fields, ['id', 'connected', 'has_gpu', 'client_ip', 'state', 'connection_state_since'])
    output_result(ctx, result.get('resources'), display_fields)


@resource_commands.command('invocations', help="Lists invocations for your organization")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--resource', default=None, required=False, help='Show invocations assigned to this resource only')
@click.option('--project', default=None, required=False, help='Show invocations assigned to this project only')
@click.option('--user', default=None, required=False, help='Show invocations submitted by this user only')
@click.option('--state', default=None, required=False, help='Show invocations in this state only')
@click.option('--fields', default=None, required=False, help='Fields to display, separated by comma, * for all fields')
@click.option('--gpu/--cpu', default=None, required=False, help='Show only invocations marked  for GPU/CPU invocations . by default lists both')
def list_invocations(ctx, org, resource, project, user, state, fields, gpu):
    from mali_commands.commons import output_result

    url = append_optional_filters_to_url('{org}/invocations'.format(org=org), resource=resource, project=project, user=user, state=state, gpu=gpu)
    result = ctx.obj.handle_api(ctx.obj, requests.get, url)
    display_fields = get_selected_fields(fields, ['id', 'state', 'project', 'gpu', 'resource', 'queued_at', 'image', 'command'])
    output_result(ctx, result.get('invocations'), display_fields)


@resource_commands.command('invocation_jobs', help="Lists invocation jobs for your organization")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--resource', default=None, required=False, help='Show invocation jobs assigned to this resource only')
@click.option('--project', default=None, required=False, help='Show invocation jobs assigned to this project only')
@click.option('--invocation', default=None, required=False, help='Show invocation jobs for this invocation only')
@click.option('--active/--inactive', default=None, required=False, help='Show only active (running) or inactive (finished and failed) jobs only. By default shows both')
@click.option('--fields', default=None, required=False, help='Fields to display, separated by comma, * for all fields')
def list_invocation_jobs(ctx, org, resource, project, invocation, active, fields):
    from mali_commands.commons import output_result

    url = append_optional_filters_to_url('{org}/invocation_jobs'.format(org=org), resource=resource, project=project, invocation=invocation, active=active)
    result = ctx.obj.handle_api(ctx.obj, requests.get, url)
    display_fields = get_selected_fields(fields, ['id', 'invocation', 'gpu', 'resource', 'state', 'last_updated_at'])
    output_result(ctx, result.get('invocation_jobs'), display_fields)


@resource_commands.command('install')
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--manager-type', type=str, default='docker', help='resource manager type. Currently only `docker` is supported.')
@click.option('--ssh-key-path', type=str, help='Path to the private ssh key to be used by the resource manager', default=None)
@click.option('--force/--no-force', default=False, help='Force installation (stops current resource manager if present')
@click.option('--resource-token', default=None, type=str, help='MissingLink resource token. One will be generated if this instance of MALI is authorized')
def install_rm(ctx, org, manager_type, ssh_key_path, force, resource_token):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    validate_running_resource_manager(ctx.obj, docker_client, force)

    pull_ml_image(ctx.obj, docker_client)
    _validate_apply_config(ctx, docker_client=docker_client, org=org, force=force, ssh_key_path=ssh_key_path, token=resource_token)
    _run_resource_manager(ctx.obj, docker_client)
    print('The resource manager is configured and running')


@resource_commands.command('setup_cloud_template', help="creates, encrypts and stores cloud config")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--arn', type=str, help='arn of the KMS encryption key')
@click.option('--ssh-key-path', type=str, help='Path to the private ssh key to be used by the resource manager', default=None)
def setup_cloud_template(ctx, org, arn, ssh_key_path):
    if ssh_key_path is None:
        ssh_key_path = click.prompt(text='SSH key path (--ssh-key-path)', default=get_ssh_path())
    if arn is None:
        arn = click.prompt(text='KMS arn', default='arn:aws:kms:us-east-2:502812207255:key/3722f00d-bc14-4993-a282-bd04e7c0ffd4')
    ssh_key = load_ssh_key(ssh_key_path)
    prefix, config_data = get_config_prefix_and_file(ctx.obj)
    ssh = encrypt_strint_with_boto_kms(ssh_key, arn)
    mali = encrypt_strint_with_boto_kms(config_data, arn)
    template = dict(mode='aws', key=arn, ssh=ssh, prefix=prefix, mali=mali)
    url = '{org}/resource_template/{name}'.format(org=org, name='default')
    ctx.obj.handle_api(ctx.obj, requests.post, url, template)


@resource_commands.command('restore_aws_template', help="restores predefined cloud configuration")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--arn', type=str, help='arn of the KMS encryption key', required=True)
@click.option('--ssh', type=(str, str, str), help='ssh key data', required=True)
@click.option('--mali', type=(str, str, str), help='mali config data', required=True)
@click.option('--prefix', type=str, help='mali prefix type', required=False)
@click.option('--token', type=str, help='mali prefix type', required=True)
@click.option('--rm-socket-server', type=str, help='web socket server', required=True)
@click.option('--rm-manager-image', type=str, required=True)
@click.option('--rm-config-volume', type=str, required=True)
@click.option('--rm-container-name', type=str, required=True)
@click.option('--region', envvar='REGION', type=str, required=True)
def apply_aws_template(ctx, org, arn, ssh, mali, prefix, token, rm_socket_server, rm_manager_image, rm_config_volume, rm_container_name, region):
    from .legit.context import Expando

    print('decrypting data')
    ssh_key = decrypt_string_with_boto_kms(ssh, region)
    mali_data = decrypt_string_with_boto_kms(mali, region)
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()

    print('building installation config')
    config = Expando()
    config.rm_socket_server = rm_socket_server
    config.rm_manager_image = rm_manager_image
    config.rm_config_volume = rm_config_volume
    config.rm_container_name = rm_container_name

    print('pulling RM')
    pull_ml_image(ctx.obj, docker_client)

    print('killing RM')
    validate_running_resource_manager(config, docker_client, True)

    print('building volume')
    if _docker_present(docker_client.volumes.get, rm_config_volume):
        docker_client.volumes.get(rm_config_volume).remove(force=True)
    docker_client.volumes.create(rm_config_volume)
    _apply_config_to_volume(config, docker_client, ssh_key, token, prefix=prefix, config_data=mali_data)

    print('Clear containers')
    for container in docker_client.containers.list():
        if container.name == rm_container_name:
            print("\t  KILL: %s" % container.id)
            container.kill()

    for container in docker_client.containers.list(all=True):
        if container.name == rm_container_name:
            print("\t  REMOVE: %s" % container.id)
            container.remove(force=True)

    print('Start RM:')
    inst = _run_resource_manager(config, docker_client)
    print('The resource manager is configured and running')
    # for line in inst.logs(stream=True):
    #     print(line.strip().decode('utf-8'))
    print('for logs run: docker logs -f %s ' % rm_container_name)
