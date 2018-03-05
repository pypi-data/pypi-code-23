import os
import unittest

from configuration import Configuration


class TestEnvironmentVariableConfiguration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
        config_dir = os.path.join(project_root, 'config')
        os.environ['CONFIG_DIR'] = config_dir
        os.environ['CONFIG_ENVS'] = 'production staging development testing'
        os.environ['CONFIG_FILES'] = 'config.yml localhost.yml secrets.yml'

    def test_default_constructor(self):
        config = Configuration()
        assert config.directory == os.environ['CONFIG_DIR']
        assert config.environments == ['production', 'staging', 'development', 'testing']
        assert config.files == ['config.yml', 'localhost.yml', 'secrets.yml']
