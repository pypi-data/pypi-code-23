import unittest
import json
import os

from docopt import docopt
from terminaltables import AsciiTable

from .. import Junc, __doc__ as doc
from .. server import ValidationError

class TestJunc(unittest.TestCase):
    def setUp(self):
        self.junc = Junc(testing = True)

    def tearDown(self):
        files = [
            self.junc.st.file_path,
            self.junc.st.file_path + '.bak',
            self.junc.st.file_path + '.custom_backup'
        ]
        for fi in files:
            if os.path.isfile(fi):
                os.remove(fi)

    def seed(self):
        """
        Adds 2 servers to the server list
        """
        servers = [
            {
                'name': 'a_valid_name',
                'username': 'a_valid_username',
                'ip': '123.456.789',
                'location': 'Pytest :)'
            },
            {
                'name': 'another_valid_name',
                'username': 'a_not_short_username',
                'ip': '321.654.987',
                'location': 'Pytest :)'
            }
        ]
        for server in servers:
            self.junc.sl.add(server)
        assert len(self.junc.sl.servers) == 2

    def test_list(self):
        self.seed()
        args = docopt(doc, ['list'])
        results = self.junc.what_to_do_with(args)
        assert type(results) is AsciiTable

        args = docopt(doc, ['list', '--json'])
        results = self.junc.what_to_do_with(args)
        assert type(results) is str
        assert json.loads(results)

    def test_add(self):
        self.seed()

        old_size = len(self.junc.sl.servers)

        args = docopt(doc, ['add', 'server_name', 'username', '123.456', 'Pytest :)'])
        results = self.junc.what_to_do_with(args)

        assert results == 'server_name added'
        assert len(self.junc.sl.servers) == old_size + 1

        with self.assertRaises(ValidationError):
            args = docopt(doc, ['add', 'valid_name', 'not@a%valid&username', '123', ''])
            self.junc.what_to_do_with(args)

            args = docopt(doc, ['add', '', 'valid_username', '', ''])
            self.junc.what_to_do_with(args)

    def test_remove(self):
        self.seed()

        old_size = len(self.junc.sl.servers)

        in_use_server_name = self.junc.sl.servers[0].name
        args = docopt(doc, ['remove', in_use_server_name])
        self.junc.what_to_do_with(args)

        assert len(self.junc.sl.servers) == old_size - 1

        with self.assertRaises(ValueError):
            args = docopt(doc, ['remove', 'not_a_server'])
            self.junc.what_to_do_with(args)

    def test_bacup(self):
        base_file = self.junc.st.file_path
        backup_file = base_file + '.bak'

        assert os.path.isfile(base_file)
        assert not os.path.isfile(backup_file)

        args = docopt(doc, ['backup'])
        self.junc.what_to_do_with(args)

        assert os.path.isfile(base_file)
        assert os.path.isfile(backup_file)

    def test_backup_to_custom_location(self):
        base_file = self.junc.st.file_path
        backup_file = base_file + '.custom_backup'

        assert os.path.isfile(base_file)
        assert not os.path.isfile(backup_file)

        args = docopt(doc, ['backup', backup_file])
        self.junc.what_to_do_with(args)

        assert os.path.isfile(base_file)
        assert os.path.isfile(backup_file)

    def test_restore(self):
        base_file = self.junc.st.file_path
        backup_file = base_file + '.bak'

        assert os.path.isfile(base_file)
        assert not os.path.isfile(backup_file)

        args = docopt(doc, ['backup'])
        self.junc.what_to_do_with(args)

        os.remove(base_file)

        assert not os.path.isfile(base_file)
        assert os.path.isfile(backup_file)

        args = docopt(doc, ['restore'])
        self.junc.what_to_do_with(args)

        assert os.path.isfile(base_file)

    def test_restore_from_custom_location(self):
        base_file = self.junc.st.file_path
        backup_file = base_file + '.custom_backup'

        assert os.path.isfile(base_file)
        assert not os.path.isfile(backup_file)

        args = docopt(doc, ['backup', backup_file])
        self.junc.what_to_do_with(args)

        os.remove(base_file)

        assert not os.path.isfile(base_file)
        assert os.path.isfile(backup_file)

        args = docopt(doc, ['restore', backup_file])
        self.junc.what_to_do_with(args)

        assert os.path.isfile(base_file)
