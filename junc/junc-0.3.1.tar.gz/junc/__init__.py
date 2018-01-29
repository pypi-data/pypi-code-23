"""
Usage:
    junc list [--json]
    junc connect <name>
    junc add [(<name> <username> <ip>)] [<location>]
    junc remove <name>
    junc backup [<file>]
    junc restore [<file>]

Options:
    -h --help     Show this screen.
    --version     Show version.
    --json        Output server list as JSON instead of a (readable) table

Arguments:
    name          Human-readable name of a server
    username      Username you wish to login with
    ip            The IP of the server
    location      (Optional) Where the server is located (useful for headless machines ie. raspberry pi)
    file          A backup is created at (or restored from) this location (default: ~/.junc.json.bak)

Notes:
    Data is stored in ~/.junc.json
    Default backup location is ~/.junc.json.bak
"""

"""
My nigga @Gambit told me I should add docstrings so i am
This will keep a json file of servers you add. It can display them as a pretty table.
The data associated with a table is as follows:
    1. Name
    2. Username
    3. IP
    4. Location (optional)
You can run `junc connect [server-name]` to ssh into a server easily
"""

import os
import sys

from docopt import docopt
from contextlib import suppress
import json

from junc.storage import Storage

def new_server(args):
    """
    Takes the docopt argument vector and returns a new server 'object'
    (Just a dictionary, not it's own class)
    """
    attr_list = ['<ip>', '<username>', '<name>', '<location>']
    new_server = {}
    for attr in attr_list:
        if attr in args.keys():
            # cut off the < and >
            pretty_attr = attr[1:-1]
            new_server[pretty_attr] = args[attr]
    return new_server

def cli(args):
    """
    Inteprets the docopt argument vector and does something cool with it
    """
    storage = Storage()
    try:
        server_list = storage.get_servers()
    except PermissionError:
        print('Error: Permission denied. Try again with sudo or change permissions on ' + storage.file_path + ' (Recommended)')
        return False

    if args['add']:
        return add(args, server_list, storage)

    if args['list']:
        return list_tables(args, server_list, storage)

    if args['connect']:
        return connect(args, server_list)

    if args['remove']:
        return remove(args, server_list, storage)

    if args['backup']:
        return backup(args, storage)

    if args['restore']:
        return restore(args, storage)

def list_tables(args, server_list, storage):
    server_table = storage.get_server_table()
    if args['--json']:
        print(json.dumps(server_list, indent=2))
        return server_list
    print(server_table)
    return server_table

def add(args, server_list, storage):
    while not args['<name>'] or not args['<ip>'] or not args['<username>']:
        args['<name>'] = input('Name: ')
        args['<username>'] = input('Username: ')
        args['<ip>'] = input('IP: ')
        args['<location>'] = input('Location: ')
        if not args['<name>'] or not args['<ip>'] or not args['<username>']:
            print('Please fill out all the fields')
            print('\n')
    server_list.append(new_server(args))
    storage.write(server_list)
    args['list'] = True

def connect(args, server_list):
    connection = ''
    for server in server_list:
        if server['name'] == args['<name>']:
            connection = server['username'] + '@' + server['ip']
    if not connection:
        print("Couldn't find that server...")
        return False
    print('Connecting...')
    os.system('ssh ' + connection)
    return True

def remove(args, server_list, storage):
    for i in range(len(server_list)):
        if server_list[i]['name'] == args['<name>']:
            print(server_list[i]['name'] + ' removed')
            del server_list[i]
            storage.write(server_list)
            return server_list
        if i == len(server_list) - 1:
            print("Couldn't find that server...")
            return False

def backup(args, storage):
    storage.backup(args['<file>'])
    return True

def restore(args, storage):
    print('This will overwrite your current', storage.file_path)
    choice = input('Are you sure? (y/n)')
    if choice in ['y', 'Y', 'yes']:
        storage.restore(args['<file>'])
        return True
    else:
        print('Canceled')
        return False

def main():
    arguments = docopt(__doc__)
    with suppress(KeyboardInterrupt):
        if not cli(arguments):
            sys.exit(1)
    print('\n')
    sys.exit(0)

if __name__ == '__main__':
    main()
