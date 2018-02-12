import unittest
import os
import json

from terminaltables import AsciiTable

from ..server import _Server, ServerList, ValidationError
from ..storage import Storage

class TestServerList(unittest.TestCase):
    def setUp(self):
        self.seed_test_data()
        self.sl = ServerList(testing = True)

    def tearDown(self):
        st = Storage(testing = True)
        if os.path.isfile(st.file_path):
            os.remove(st.file_path)

    def seed_test_data(self):
        servers = [
            _Server({
                'name': 'sween',
                'username': 'pi',
                'ip': '192.168.0.134',
                'location': 'Dining Room'
            }),
            _Server({
                'name': 'another',
                'username': 'pi',
                'ip': '192.168.0.138',
                'location': 'Attic'
            })
        ]
        st = Storage(testing = True)
        st.write(servers)

    def test_it_has_a_server_list(self):
        assert self.sl.servers
        assert type(self.sl.servers[0]) is _Server

    def test_ip_validation(self):
        # Addresses can be pretty much anything
        # it could be 1.1.1.1
        # Or https://us-west-2.console.aws.amazon.com/elasticbeanstalk/home?region=us-west-2#/environment/dashboard?applicationName=somethinghere&environmentId=e-234h8df
        # I check that it's not an empty string
        with self.assertRaises(ValueError):
            self.sl.validate_ip('')

    def test_username_validation(self):
        with self.assertRaises(ValueError):
            self.sl.validate_username("username_with_@_in_it")
            self.sl.validate_username("username_with_^_in_it")
            self.sl.validate_username("username_with_*_in_it")
            self.sl.validate_username("username_with_$#@!@#$%^&*(^%$%^&*(_in_it")
            self.sl.validate_username("you_get_the_f$#%ing_picture")

    def test_add(self):
        old_size = len(self.sl.servers)
        new_server = _Server({
            'name': 'anotherone?',
            'username': 'totallyvalid',
            'ip': '123.456.789',
            'location': ''
        })
        self.sl.add(new_server)
        assert len(self.sl.servers) == old_size + 1

    def test_remove(self):
        with self.assertRaises(ValueError):
            self.sl.remove('namenotfoundlmao')

        old_size = len(self.sl.servers)
        assert old_size
        self.sl.remove('sween')
        assert len(self.sl.servers) == old_size - 1

        # I ran into this bug, added some tests to make sure it doesn't happen again
        refreshed = self.sl.get()
        assert 'sween' not in [ser.name for ser in refreshed]

    def test_write(self):
        file_path = Storage(testing = True).file_path
        assert os.path.getsize(file_path) > 0
        assert len(self.sl.servers) > 0

        with open(file_path, 'w') as fi:
            fi.truncate(0)

        assert os.path.getsize(file_path) == 0

        self.sl.save()

        assert os.path.getsize(file_path) > 0

    def test_server_table(self):
        assert type(self.sl.as_table()) is AsciiTable

    def test_name_validation(self):
        # Get a name thats already in use
        name = self.sl.servers[0].name
        with self.assertRaises(ValidationError):
            self.sl.validate_name(name)

    def test_server_list_as_json(self):
        assert json.loads(self.sl.as_json())
