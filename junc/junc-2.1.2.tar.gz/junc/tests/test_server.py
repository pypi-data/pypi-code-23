import unittest

from ..server import _Server

class TestServer(unittest.TestCase):
    """
    The _Server class can't really do anything, it's just a place to store data.
    Will probably be expanded in the future. Right now it's a shell.
    """
    def test_make_one(self):
        server_deets = {
            'name': 'a_valid_name',
            'username': 'a_valid_username',
            'ip': '123.456.789',
            'location': 'Pytest :)'
        }
        server = _Server(server_deets)
        assert type(server) is _Server

    def test_serialize(self):
        server_deets = {
            'name': 'a_valid_name',
            'username': 'a_valid_username',
            'ip': '123.456.789',
            'location': 'Pytest :)'
        }
        server = _Server(server_deets)
        server.extra = 'some extra data that we dont really care about'
        for key in server_deets:
            assert key in server.__dict__.keys()

    def test_address(self):
        server = _Server({
            'name': 'doesntmatter',
            'username': 'luke',
            'ip': '123.456.789',
            'location': 'Pytest :)'
        })
        assert server.address() == server.username + "@" + server.ip
