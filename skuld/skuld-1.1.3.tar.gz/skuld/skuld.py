#!/usr/bin/env python3

import argparse
import configparser
import json
import os
import os.path as path
import pathlib
import sys

VERSION = "0.0.0"

if sys.version_info[0] < 3:
    raise RuntimeError('Must be using Python 3')

parser = argparse.ArgumentParser(description='Managing access to AWS with MFA; version ' + VERSION)


def user_name(profile):
    user = json.loads(os.popen('aws --profile=%s sts get-caller-identity' % profile).read())['Arn']
    return user.split(':user/')[1]


def mfa_device(profile):
    user = user_name(profile)
    mfas = json.loads(os.popen('aws --profile=%s iam list-mfa-devices --user-name %s' % (profile, user)).read())
    return mfas['MFADevices'][0]['SerialNumber']


def fetch_sts_credentials(profile, mfa, token):
    seconds = 1800 if profile.endswith('-adm') else 36000
    return json.loads(os.popen(
        'aws --profile %s  sts get-session-token --serial-number %s --duration-seconds %s --token-code %s' %
        (profile, mfa, seconds, token)).read())['Credentials']


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


def compute_region(args, profile):
    if args.region:
        return args.region
    else:
        config = read_credentials()
        return config[profile]['region']


def write_credentials(mfa_profile, credentials, region):
    creds = read_credentials()
    creds[mfa_profile] = {'aws_access_key_id': credentials['AccessKeyId'],
                          'aws_secret_access_key': credentials['SecretAccessKey'],
                          'aws_session_token': credentials['SessionToken'],
                          'region': region}
    with open(credentials_path(), 'w') as configfile:
        creds.write(configfile)


def write_config(mfa_profile, region):
    config = read_config()
    config[mfa_profile] = {'region': region}
    with open(config_path(), 'w') as configfile:
        config.write(configfile)


def main():
    parser.add_argument('profile', type=str, help="profile against which to acquire the sts")
    parser.add_argument('-r', '--region', type=str, help="override the region for the mfa profile")
    args = parser.parse_args()
    profile = args.profile
    mfa_profile = profile + '-skuld'
    mfa = mfa_device(args.profile)
    token = input("Enter your token: ")
    credentials = fetch_sts_credentials(profile, mfa, token)
    region = compute_region(args, profile)
    write_credentials(mfa_profile, credentials, region)
    write_config(mfa_profile, region)
    print('Credentials valid until: ' + credentials['Expiration'])


if __name__ == "__main__":
    main()
