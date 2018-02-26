import unittest

import requests
from requests import Timeout

from httpstatuspuppet.helpers import get_open_port
from httpstatuspuppet.server import Server


def _is_server_running(server: Server) -> bool:
    """
    Checks if the given server is running.
    :param server: the server to check if running
    :return: whether the server is running
    """
    try:
        requests.get(server.url, timeout=0.1)
        return True
    except Timeout:
        return False


class TestServer(unittest.TestCase):
    """
    Tests for `Server`.
    """
    def setUp(self):
        self.server = Server(port=get_open_port())
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_status_codes(self):
        for status_code in range(101, 600):
            with self.subTest(status_code=status_code):
                response = requests.get(f"{self.server.url}/{status_code}")
                self.assertEqual(status_code, response.status_code)

    def test_non_numeric_status_code(self):
        response = requests.get(f"{self.server.url}/kittens")
        self.assertEqual(400, response.status_code)

    def test_out_of_range_status_code(self):
        response = requests.get(f"{self.server.url}/99999")
        self.assertEqual(400, response.status_code)

    def test_start_when_started(self):
        assert _is_server_running(self.server)
        self.server.start()
        self.assertTrue(_is_server_running(self.server))

    def test_stop_when_started(self):
        assert _is_server_running(self.server)
        self.server.stop()
        self.assertFalse(_is_server_running(self.server))

    def test_stop_when_stopped(self):
        self.server.stop()
        assert not _is_server_running(self.server)
        self.server.stop()
        self.assertFalse(_is_server_running(self.server))


if __name__ == "__main__":
    unittest.main()
