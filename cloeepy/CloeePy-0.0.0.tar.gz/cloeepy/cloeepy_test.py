import os
import unittest

from cloeepy.cloeepy import CloeePy

class TestCloeePy(unittest.TestCase):

    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), "data/test-config.yml")
        os.environ["CLOEEPY_CONFIG_PATH"] = config_path

    def test_init(self):
        c = CloeePy()
        self.assertTrue(hasattr(c, "log"))
        self.assertTrue(hasattr(c, "config"))

if __name__ == "__main__":
    unittest.main()
