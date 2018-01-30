"""Encrypt and decrypt data using KMS keys.

Reads configuration from the ``kms`` key.

Configuration
-------------

The ``targets`` key specifies a map for each target.

Each target can have the following keys:

:``file``:        The file to encypt to, or decrypt from.
:``key``:         The KMS key name to use.
:``data-key``:    The data-key to decrypt to.
:``format``:      The format to parse the data as for data-key.
:``plain-file``:  The file to decrypt to, or encrypt from.
:``encode``:      Encoding for encrypted file (none, or base64).
:``region_name``: AWS region for KMS key.

:``context``: A list of configuration names that will be used to generate an
              encryption context.  The default is ``[project]``.

:``envelope``: The file to write the encypted key to.  If no envelope is
               specified, then the data is encrypted with the KMS key
               directly (4Kb limit).


Tasks
-----

:``encrypt``:      is used to encrypt a file.
:``decrypt``:      is used to decrypt a file.
:``decrypt-data``: is used to decrypt a file to a ``data`` key in menhir.

"""
import argparse
import json
import logging
import subprocess
from base64 import b64decode, b64encode
from os.path import exists

import boto3

from menhir.fileutils import load_encrypted, slurp_bytes, spit_bytes
from menhir.tool import Tool
from menhir.tool_config import aliased_value_array
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
)
from menhir.utils import getd, method, multi, select_keys

from ruamel.yaml import YAML

log = logging.getLogger(__name__)


def tool():
    return Kms()


class Kms(Tool):

    def dir_info(tool, path, info):
        return {
            'project_recognised': False,
            'can_run': True,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build task."""
        return task(path, info, args)


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to encrypt and decrypt data using KMS",
        **kwargs
    )
    parsers = parser.add_subparsers(help="Kms commands", dest='task')

    p = parsers.add_parser(
        'encrypt-file',
        help='Encrypt a file to using a KMS key.'
    )
    p.add_argument('-p', '--plain-file', help="Source file to encrypt")

    g = p.add_mutually_exclusive_group()
    g.add_argument('-f', '--file', help="File name for the encrypted data")
    g.add_argument('-t', '--target', help="Target name")

    p.add_argument('-k', '--key', help="KMS key name")
    p.add_argument('-e', '--envelope', help="File name for the encrypted key")
    p.add_argument(
        '-c', '--context',
        help="Specify a list of config keys for the encryption context"
    )
    p.add_argument(
        '-n', '--encode',
        choices=['none', 'base64'],
        help="Encode encrypted file"
    )
    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the encryption settings")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'decrypt-file',
        help='Decrypt a file to using a KMS key.'
    )

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('-t', '--target', help="Target name")
    g.add_argument('-f', '--file', help="Encrypted data file name")

    g = p.add_mutually_exclusive_group()
    g.add_argument(
        '-p', '--plain-file',
        help="File to write the decrypted data to"
    )
    g.add_argument('-d', '--data-key', help="Menhir data key to write to")
    p.add_argument(
        '-m', '--format',
        help="Format to parse data written to key"
    )

    p.add_argument('-k', '--key', help="KMS key name")
    p.add_argument('-e', '--envelope', help="File name for the encrypted key")
    p.add_argument(
        '-c', '--context',
        help="Specify a list of config keys for the encryption context"
    )
    p.add_argument(
        '-n', '--encode',
        choices=['none', 'base64'],
        help="Encrypted file is encoded"
    )
    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the decryption settings")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(path, info, args):
    log.debug("kms task: %s", args.task)
    return args.task


@method(task, 'encrypt-file')
def task_encrypt(path, info, args):
    if not (args.target or args.file):
        log.error('No target or file specified')
        return FAIL

    config = info.get('kms', {}).get('targets', {}).get(args.target, {})

    arg_dict, status = target_args(config, args)
    log.debug("arg_dict %s", arg_dict)
    if status != OK:
        return status

    encrypt_config_for_args(config, args)

    key = config.get('key')
    if not key:
        log.error(
            'No KMS encryption key name specified for target %s',
            config.get('file')
        )
        return FAIL

    values_list = aliased_value_array(
        config.get('context', []),
        info,
        path,
        arg_dict,
    )
    context = {k: v for k, v in values_list}

    arg_dict.update(context)
    expand_keys(config, arg_dict)

    log.debug('encrypt: %s', config)
    if config.get('envelope'):
        return encrypt_with_envelope(config, context)
    else:
        return encrypt_with_master(config, context)


def encrypt_config_for_args(config, args):
    if args.file:
        config['file'] = args.file
    if args.encode:
        config['encode'] = args.encode
    if args.key:
        config['key'] = args.key
    if args.plain_file:
        config['plain-file'] = args.plain_file
    if args.envelope:
        config['envelope'] = args.envelope
    if args.context:
        config['context'] = list(map(
            lambda x: x.strip(),
            args.context.split(",")
        ))


def encrypt_with_master(config, context):
    data = slurp_bytes(config['plain-file'])
    client_config = select_keys(config, ['region_name'])
    kms = boto3.client('kms', **client_config)
    res = kms.encrypt(
        KeyId=config['key'],
        Plaintext=data,
        EncryptionContext=context,
    )
    encode = config.get('encode', 'base64')
    if encode == 'none':
        data = res['CiphertextBlob']
    elif encode == 'base64':
        data = b64encode(res['CiphertextBlob'])

    spit_bytes(config['file'], data)
    return OK


def encrypt_with_envelope(config, context):
    client_config = select_keys(config, ['region_name'])
    kms = boto3.client('kms', **client_config)
    envelope_path = config['envelope']
    if exists(envelope_path):
        data = slurp_bytes(envelope_path)
        data = b64decode(data)
        key = kms.decrypt(
            CiphertextBlob=data,
            EncryptionContext=context,
        )
        plain_key = key['Plaintext']
    else:
        key = kms.generate_data_key(
            KeyId=config['key'],
            KeySpec='AES_256',
            EncryptionContext=context,
        )
        plain_key = key['Plaintext']
        enc_key = b64encode(key['CiphertextBlob'])
        spit_bytes(envelope_path, enc_key)

    return local_encrypt(
        plain_key,
        config['plain-file'],
        config['file'])


def local_encrypt(key, source, dest):
    res = subprocess.call([
        "openssl", "aes-256-cbc", "-a",
        "-k", key,
        "-in", source,
        "-out", dest
    ])
    if res == 0:
        return OK
    return FAIL


@method(task, 'decrypt-file')
def task_decrypt(path, info, args):
    if not (args.target or args.file):
        log.error('No target or encrypted file specified')
        return FAIL

    config = info.get('kms', {}).get('targets', {}).get(args.target, {})
    if args.target and not config:
        log.debug("kms decrypt: nothing to do for target %s", args.target)
        return NOTHING_TO_DO

    arg_dict, status = target_args(config, args)
    log.debug("arg_dict %s", arg_dict)
    if status != OK:
        return status

    decrypt_config_for_args(config, args)

    key = config.get('key')
    if not key:
        log.error(
            'No KMS decryption key name specified for target file %s',
            config['file']
        )
        return FAIL

    values_list = aliased_value_array(
        config.get('context', []),
        info, path, arg_dict
    )
    context = {k: v for k, v in values_list}

    arg_dict.update(context)
    expand_keys(config, arg_dict)

    log.debug('decrypt: %s', config)
    if config.get('envelope'):
        return decrypt_with_envelope(path, info, config, context)
    else:
        return decrypt_with_master(path, info, config, context)


def decrypt_config_for_args(config, args):
    if args.file:
        config['file'] = args.file
    if args.plain_file:
        config['plain_file'] = args.plain_file

    if args.key:
        config['key'] = args.key
    if args.data_key:
        config['data-key'] = args.data_key
    if args.format:
        config['format'] = args.format
    if args.envelope:
        config['envelope'] = args.envelope
    if args.encode:
        config['encode'] = args.key
    if args.context:
        config['context'] = list(map(
            lambda x: x.strip(),
            args.context.split(",")
        ))


def decrypt_with_master(path, info, config, context):
    data = slurp_bytes(config['file'])
    if config.get('encode', 'base64') == 'base64':
        data = b64decode(data)
    client_config = select_keys(config, ['region_name'])
    kms = boto3.client('kms', **client_config)
    res = kms.decrypt(
        CiphertextBlob=data,
        EncryptionContext=context,
    )
    data_key = config.get('data-key')
    if data_key and not config.get('plain_file'):
        data = res['Plaintext']
        log.debug('data is %s', data)
        parse_as = config.get('format', 'json')
        if parse_as == 'json':
            data = json.loads(data)
        elif parse_as == 'yaml':
            yaml = YAML()
            data = yaml.load(data)
        else:
            log.error('Unknown foramt %s', parse_as)
            return FAIL
        getd(info, 'data')[data_key] = data
    else:
        spit_bytes(config['plain_file'], res['Plaintext'])

    return OK


def decrypt_with_envelope(path, info, config, context):
    client_config = select_keys(config, ['region_name'])
    kms = boto3.client('kms', **client_config)
    enc_key = b64decode(slurp_bytes(config['envelope']))
    key = kms.decrypt(
        CiphertextBlob=enc_key,
        EncryptionContext=context,
    )
    data_key = config.get('data-key')

    if data_key and not config.get('plain_file'):
        data = load_encrypted(config['file'], key['Plaintext'])
        parse_as = config.get('format', 'json')
        if parse_as == 'json':
            data = json.loads(data)
        elif parse_as == 'yaml':
            yaml = YAML()
            data = yaml.load(data)
        else:
            log.error('Unknown foramt %s', parse_as)
            return FAIL
        getd(info, 'data')[data_key] = data
        return OK
    else:
        return local_decrypt(
            key['Plaintext'],
            config['file'],
            config['plain_file']
        )


def local_decrypt(key, source, dest):
    res = subprocess.call([
        "openssl", "aes-256-cbc", "-a", "-d",
        "-k", key,
        "-in", source,
        "-out", dest
    ])
    if res == 0:
        return OK
    return FAIL


def target_args(config, args):
    """Return the target arguments as a dict."""
    expected_args = config.get('args', [])
    actual_args = args.args or []
    if len(expected_args) != len(actual_args):
        log.error('Exepcted decrypt --arg for each of %s', expected_args)
        return None, FAIL
    else:
        return {k: v for (k, v) in zip(expected_args, actual_args)}, OK


def expand_keys(config, arg_dict):
    for k in ['file', 'key', 'plain_file', 'envelope', 'region_name']:
        v = config.get(k)
        if v:
            config[k] = v % arg_dict
