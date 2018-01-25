import unittest
import imqfody


class SimpleTests(unittest.TestCase):
    def setUp(self):
        self.client = imqfody.IMQFody(
            url='http://192.168.192.137:8666',
            username='intelmq',
            password='intelmq'
        )

    def tearDown(self):
        # This is just to prevent resource warnings in the tests, requests.Session don't have to get closed manually
        self.client._session.close()

    def test_ping(self):
        self.assertGreater(len(self.client.ping()), 0, 'Answer to ping is too short.')
        self.assertEqual(self.client.ping(), ['pong'], 'Ping test failed.')
