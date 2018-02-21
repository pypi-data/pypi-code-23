"""
Usage:
    junc list [--json] [--debug]
    junc connect <name> [--debug]
    junc add <name> <username> <ip> [<location>] [--debug]
    junc remove <name> [--debug]
    junc backup [<file>] [--debug]
    junc restore [<file>] [--debug]

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

    You need to have 'ssh' installed on your system.
"""

import os
import json

from docopt import docopt
from terminaltables import AsciiTable

# I hate these lines
# One is for pytest, one if for python
# idk why i have to do this
try:
    from storage import Storage
    from server import ServerList
except ImportError:
    from .storage import Storage
    from .server import ServerList

def confirm(message="Sure? "): # pragma: no cover
    while True:
        choice = input(message + ' [y/n]: ')
        if choice.upper() == 'Y':
            return True
        elif choice.upper() == 'N':
            return False
        else:
            print("Valid choices are y or n")

class Junc(object):
    """
    Handles the docopt args and connects to servers
    """
    def __init__(self, testing = False):
        self.st = Storage(testing = testing)
        self.sl = ServerList(testing = testing)

    def what_to_do_with(self, args):
        """
        Inteprets the docopt argument vector and does something cool with it.
        Returns what will be printed to the console after the command is run.
        """
        if args['list']:
            return self.sl.as_json() if args['--json'] else self.sl.as_table()

        if args['add']:
            self.sl.add({
                'name': args['<name>'],
                'ip': args['<ip>'],
                'username': args['<username>'],
                'location': args['<location>']
            })
            self.sl.save()
            return self.sl.as_table()

        if args['remove']:
            self.sl.remove(args['<name>'])
            return args['<name>'] + ' removed'

        if args['connect']:
            self.connect(args['<name>'])

        if args['backup']:
            self.st.backup(args['<file>'])
            return ''

        if args['restore']:
            self.st.restore(args['<file>'])
            return ''

    def connect(self, name):
        connection = ''
        for server in self.sl.servers:
            if server.name == name:
                connection = server.address()
        if not connection:
            return "Couldn't find that server..."
        print('Connecting...')
        os.system('ssh ' + connection)
        return 'Done'

def main():
    args = docopt(__doc__)
    junc = Junc(testing = args['--debug'])
    try:
        results = junc.what_to_do_with(args)
        if type(results) is AsciiTable:
            print(results.table)
        else:
            print(results)
    except Exception as mess: # This makes me cringe
        # Unless we're debugging...
        if args['--debug']:
            raise
        # Print the message of the exception, not the full error
        # More user friendly
        print(mess)

if __name__ == '__main__':
    main()
