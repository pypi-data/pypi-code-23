import json
from shutil import copy2
import os

from coolered import color
from terminaltables import AsciiTable

class Storage():
    """
    Handles storing and retrieving of server data
    """
    def __init__(self):
        self.file_path = os.path.join(os.path.expanduser("~"), ".junc.json")
        self.create_file(self.file_path)

    def create_file(self, file_path):
        """
        Creates the storage file if it doesn't exist
        """
        try:
            open(file_path, 'a')
        except PermissionError:
            print("Error: Permission denied. Change permissions on " + file_path)
        return True

    def write(self, server_list):
        """
        Writes a whole server list to the storage file
        """
        with open(self.file_path, 'w') as f:
            json.dump(server_list, f, indent=4)
        return True

    def get_servers(self):
        try:
            return json.loads(open(self.file_path, 'r').read())
        except json.decoder.JSONDecodeError:
            return []

    def get_server_table(self):
        """
        Gets all the servers and plops them into a terminal table
        """
        server_list = self.get_servers()
        if not server_list:
            return "No Servers yet :(\nAdd some!"
        table_data = [
            ['Name', "Address", "Location"],
        ]
        for server in server_list:
            table_data.append([server['name'], server['username'] + "@" + server['ip'], server['location']])
        return AsciiTable(table_data).table

    def backup(self, location=None, reverse=False):
        """
        Copies the contents of the storage file to the location variable
        Default is the storage file with '.bak' appended to the path
        """
        if not location:
            location = self.file_path + '.bak'
        if reverse:
            print('Restoring to', self.file_path)
            copy2(location, self.file_path)
            color('green', 'Done')
        else:
            print('Backing up to', location)
            copy2(self.file_path, location)
            color('green', 'Done')

    def restore(self, location=None):
        """
        'Backup' the backup to the regular storage file
        """
        self.backup(location, True)
