import os.path
import sqlite3

from django.conf import settings

from .base import BaseDbdevBackend

DBSETTINGS = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'dbdev_tempdata/SqliteBackend/dbdev.sqlite3'
}


class SqliteBackend(BaseDbdevBackend):
    def init(self):
        if os.path.exists(self.datadir):
            self.stderr.write('The data directory ({}) already exists.'.format(self.datadir))
            raise SystemExit()
        else:
            self.create_datadir_if_not_exists()

    def destroy(self):
        if os.path.exists(self.datadir):
            self.remove_datadir()
            self.stdout.write('Successfully removed "{}".'.format(self.datadir))

    @property
    def sqlite3_cli_command(self):
        return 'sqlite3'

    @property
    def database_file_path(self):
        return settings.DATABASES['default']['NAME']

    def get_sqlite3_connection(self):
        return sqlite3.connect(self.database_file_path)

    def run_database_server_in_foreground(self):
        pass

    def start_database_server(self):
        pass

    def stop_database_server(self):
        pass

    def load_dbdump(self, dumpfile):
        connection = self.get_sqlite3_connection()
        with open(dumpfile, 'r') as f:
            connection.executescript(f.read())

    def create_dbdump(self, dumpfile):
        connection = self.get_sqlite3_connection()
        with open(dumpfile, 'w') as f:
            for line in connection.iterdump():
                f.write('{}\n'.format(line))

    def backup(self, directory):
        backupfile = os.path.join(directory, 'backup.sql')
        self.create_dbdump(backupfile)

    def restore(self, directory):
        backupfile = os.path.join(directory, 'backup.sql')
        self.load_dbdump(backupfile)

    def serverinfo(self):
        self.stdout.write('Showing server info for sqlite3 makes not sense - it is not a server.')
