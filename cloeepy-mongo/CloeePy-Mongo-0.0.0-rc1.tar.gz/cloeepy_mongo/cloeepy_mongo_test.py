import os
import unittest
from cloeepy import CloeePy
from cloeepy_mongo.cloeepy_mongo import CloeePyMongo

class TestCloeePyMongo(unittest.TestCase):

    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), "data/config.yml")
        os.environ["CLOEEPY_CONFIG_PATH"] = config_path

    def test_init(self):
        c = CloeePy()
        self.assertTrue(hasattr(c, "log"))
        self.assertTrue(hasattr(c, "config"))
        self.assertTrue(hasattr(c, "mongo"))        

if __name__ == "__main__":
    unittest.main()
