import os
import unittest
import boto3
from cloeepy import CloeePy
from cloeepy_boto.cloeepy_boto import CloeePyBoto

class TestCloeePyBoto(unittest.TestCase):

    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), "data/config.yml")
        os.environ["CLOEEPY_CONFIG_PATH"] = config_path

    def test_init(self):
        app = CloeePy()
        self.assertTrue(hasattr(app, "log"))
        self.assertTrue(hasattr(app, "config"))
        self.assertTrue(hasattr(app, "boto"))
        self.assertTrue(isinstance(app.boto, boto3.Session))

if __name__ == "__main__":
    unittest.main()
