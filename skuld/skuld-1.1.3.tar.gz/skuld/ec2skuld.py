#!/usr/bin/env python3

import argparse
import configparser
import json
import os
import os.path as path
import pathlib
import requests
import sys

VERSION = "0.0.0"
SKULD_PROFILE_NAME = 'skuld'

if sys.version_info[0] < 3:
    raise RuntimeError('Must be using Python 3')

parser = argparse.ArgumentParser(description='Managing access to AWS with MFA; version ' + VERSION)


def ec2_region(args):
    if args.region:
        return args.region
    else:
        return requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document',
                            timeout=(3.05, 10)).json()['region']


def fetch_sts_credentials(role):
    return json.loads(os.popen(
        'aws sts assume-role --role-arn %s --role-session-name neutron-core-access' % role).read())['Credentials']


def credentials_path():
    return path.join(pathlib.Path.home(), '.aws', 'credentials')


def config_path():
    return path.join(pathlib.Path.home(), '.aws', 'config')


def read_credentials():
    config = configparser.ConfigParser()
    config.read(credentials_path())
    return config


def read_config():
    config = configparser.ConfigParser()
    config.read(config_path())
    return config


def write_credentials(credentials, region):
    creds = read_credentials()
    creds[SKULD_PROFILE_NAME] = {'aws_access_key_id': credentials['AccessKeyId'],
                                 'aws_secret_access_key': credentials['SecretAccessKey'],
                                 'aws_session_token': credentials['SessionToken'],
                                 'region': region}
    with open(credentials_path(), 'w') as configfile:
        creds.write(configfile)


def write_config(region):
    config = read_config()
    config[SKULD_PROFILE_NAME] = {'region': region}
    with open(config_path(), 'w') as configfile:
        config.write(configfile)


def main():
    parser.add_argument(
        'role', type=str,
        help="role against which to acquire the sts")
    parser.add_argument('-r', '--region', type=str, help="override the region for the mfa profile")
    args = parser.parse_args()
    role = args.role
    os.makedirs(path.join(pathlib.Path.home(), '.aws'))
    region = ec2_region(args)
    credentials = fetch_sts_credentials(role)
    write_credentials(credentials, region)
    write_config(region)


if __name__ == "__main__":
    main()
