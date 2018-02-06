import unittest
import os
import json

from docopt import docopt
from terminaltables import AsciiTable

from .. import Junc, __doc__ as doc

class TestJunc(unittest.TestCase):
    def setUp(self):
        self.junc = Junc(testing = True)

    def tearDown(self):
        base_path = os.path.join(os.path.expanduser('~'), '.junc.json.test')
        files = [
            base_path,
            base_path + '.test'
        ]
        for fi in files:
            if os.path.isfile(fi):
                os.remove(fi)

    def seed_test_file(self):
        servers = [
            {
                "username": "pi",
                "ip": "192.168.0.134",
                "name": "sween",
                "location": "Dining Room"
            },
            {
                "username": "pi",
                "ip": "192.168.0.169",
                "name": "brewpi-prod",
                "location": "Brew Rig"
            }
        ]
        with open(self.junc.st.file_path, 'w') as fi:
            fi.write(json.dumps(servers))

    def test_list_servers(self):
        args = docopt(doc, ['list'])
        results = self.junc.what_to_do_with(args)

        assert type(results) is AsciiTable

        args = docopt(doc, ['list', '--json'])
        results = self.junc.what_to_do_with(args)

        print(results)
        assert type(results) is str

    def test_new_server(self):
        args = docopt(doc, ['add', 'server-name', 'username', '123.456.789', 'right here'])
        server = self.junc.new_server(args)
        assert type(server) is dict
        for item in ['name', 'username', 'ip', 'location']:
            assert item in server.keys()
            assert type(server[item]) is str

    def test_remove_server(self):
        servers = [
            {
                'name': 'to_remove',
                'ip': '19213.1235',
                'username': 'doesnt matter',
                'location': 'this really doesnt matter'
            },
            {
                'name': 'another one',
                'ip': '19213.1235',
                'username': 'doesnt matter',
                'location': 'this really doesnt matter'
            }
        ]
        self.junc.servers = servers
        self.junc.save()
        old_size = len(self.junc.st.get_servers())
        args = docopt(doc, ['remove', 'to_remove'])
        self.junc.what_to_do_with(args)

        assert len(self.junc.st.get_servers()) == old_size - 1
