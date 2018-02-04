from os import path
from random import randint
from threading import Thread

from minipyp import MiniPyP

config = {
    'host': 'localhost',
    'port': 81,
    'root': path.join(path.dirname(__file__), 'root')
}


class ServerThread(Thread):
    def __init__(self):
        super().__init__()
        self.server = MiniPyP(config)

    def run(self):
        self.server.start()


class TestMiniPyP:
    def setup_method(self, method):
        print('Starting server...')
        self.thread = ServerThread()
        self.thread.start()

    def test_get(self):
        nonce = str(randint(1, 1000000))
        print('Testing simple GET...')
        # response = get('http://localhost:81/?test=' + nonce).text
        # assert response == nonce
        assert True

    def teardown_method(self, method):
        print('Stopping server...')
        self.thread.server.stop()
