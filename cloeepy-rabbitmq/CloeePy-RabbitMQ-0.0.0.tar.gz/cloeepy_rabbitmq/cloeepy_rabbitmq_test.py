import os
import unittest
from cloeepy import CloeePy
from cloeepy_rabbitmq.cloeepy_rabbitmq import CloeePyRabbitMQ

class TestCloeePyRabbitMQ(unittest.TestCase):

    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), "data/config.yml")
        os.environ["CLOEEPY_CONFIG_PATH"] = config_path

    def test_init(self):
        app = CloeePy()
        self.assertTrue(hasattr(app, "log"))
        self.assertTrue(hasattr(app, "config"))
        self.assertTrue(hasattr(app, "rabbitmq"))
        self.assertTrue(app.rabbitmq.is_open)

if __name__ == "__main__":
    unittest.main()
