"""
Usage:
    junc list [--json]
    junc connect <name>
    junc add <name> <username> <ip> [<location>]
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

import os
import json

from docopt import docopt
from terminaltables import AsciiTable

try:
    from storage import Storage
except ImportError:
    from .storage import Storage

def confirm(message):
    while True:
        choice = input(message + ' [y/n]: ')
        if choice.upper() == 'Y':
            return True
        elif choice.upper() == 'N':
            return False
        else:
            print("Valid choices are y or n")

class Junc(object):
    def __init__(self, testing=False):
        self.st = Storage(testing=testing)

        self.servers = self.st.get_servers()

    def save(self):
        self.st.write(self.servers)

    def find_similar_server(self, args):
        """
        Returns a list of similarities between input and servers, so there won't be any duplicate servers
        """
        similarities = []
        for server in self.servers:
            if server['name'] == args['<name>']:
                similarities.append('name')
            if server['username'] == args['<username>'] and server['ip'] == args['<ip>']:
                similarities.append('address')
        return similarities

    def what_to_do_with(self, args):
        """
        Inteprets the docopt argument vector and does something cool with it
        """
        if args['list']:
            return self.list_servers(raw=args['--json'])

        if args['add']:
            similarities = self.find_similar_servers(args)
            if 'name' in similarities:
                return "There's already a server with that name, try another"
            if 'address' in similarities:
                if not confirm("A server exists with the same address. Add this one too?"):
                    return 'Server not added'

            server = self.new_server(args)
            self.servers.append(server)
            self.save()
            return server['name'] + ' added'

        if args['remove']:
            if self.remove(args['<name>']):
                return args['<name>'] + ' removed'
            return ''

        if args['connect']:
            self.connect(args['<name>'])

        if args['backup']:
            self.st.backup(args['<file>'])
            return ''

        if args['restore']:
            self.st.restore(args['<file>'])
            return ''

    def remove(self, name):
        for i in range(len(self.servers)):
            if self.servers[i]['name'] == name:
                del self.servers[i]
                self.save()
                return True
            if i == len(self.servers) - 1:
                print("Couldn't find that server...")
                return False

    def list_servers(self, raw=False):
        if raw:
            return json.dumps(self.servers)
        else:
            return self.get_server_table()

    def new_server(self, args):
        # Don't have to validate, docopt does that for us
        attrs = ['<ip>', '<username>', '<name>', '<location>']
        new_server = {}
        for attr in attrs:
            new_server[attr[1:-1]] = args[attr]
        return new_server

    def get_server_table(self):
        """
        Gets all the servers and plops them into a terminal table
        """
        table_data = [
            ['Name', "Address", "Location"],
        ]
        if not self.servers:
            table_data.append(["No Servers yet :(\nAdd some!"])
        else:
            for server in self.servers:
                table_data.append(
                    [server['name'], server['username'] + "@" + server['ip'], server['location']])
        return AsciiTable(table_data)

    def connect(self, name):
        connection = ''
        for server in self.servers:
            if server['name'] == name:
                connection = server['username'] + '@' + server['ip']
        if not connection:
            return "Couldn't find that server..."
        print('Connecting...')
        os.system('ssh ' + connection)
        return 'Done'

def main():
    args = docopt(__doc__)
    junc = Junc()
    results = junc.what_to_do_with(args)
    if type(results) is AsciiTable:
        print(results.table)
    else:
        print(results)

if __name__ == '__main__':
    main()
