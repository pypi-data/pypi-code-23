#!/usr/bin/env python3

# ./parse-ssh-config.py -f ssh-like-config fit01 desktop
# config file defaults to ~/.ssh/config



import sys
import os
import paramiko

def foo(hostname, config_filename=None):

#    client = paramiko.SSHClient()
#    client._policy = paramiko.WarningPolicy()
#    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
    config_filename = config_filename or os.path.expanduser("~/.ssh/config")
    ssh_config = paramiko.SSHConfig()
    if not os.path.exists(config_filename):
        print("Cannot open {}".format(config_filename))
        return
    with open(config_filename) as f:
        print("opening config file {}".format(config_filename))
        ssh_config.parse(f)

    user_config = ssh_config.lookup(hostname)

    print(10*'+', "In {}: found config for host {}:".format(config_filename, hostname))
    for k,v in user_config.items():
        print("{} -> {}".format(k, v))

    # client.connect(**cfg)

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-f', '--config-file', default=None)
    parser.add_argument('hostname', nargs='+')
    args = parser.parse_args()
    for hostname in args.hostname:
        foo(hostname, args.config_file)

main()    
