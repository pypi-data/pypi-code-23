import os
import unittest

from cloeepy.config import Config, obj

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "data/test-config.yml")
        os.environ["CLOEEPY_CONFIG_PATH"] = self.config_path

    def test_init(self):
        c = Config()
        self.assertEqual(c._path, self.config_path)
        self.assertTrue(isinstance(c._config_dict, dict))
        self.assertTrue(isinstance(c.CloeePy, obj))
        self.assertTrue(isinstance(c.CloeePy.Logging, obj))

if __name__ == "__main__":
    unittest.main()
