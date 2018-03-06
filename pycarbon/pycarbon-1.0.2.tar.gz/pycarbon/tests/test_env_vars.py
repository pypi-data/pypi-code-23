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

    def test_os_environment_fallback_values(self):
        config = Configuration()

        # in most cases a config value is perfect, even with environmental control to determine which env value we use
        assert config.get('XKCD_PASSWORD') == 'correct horse battery staple'

        # using containers and environment variables can prove an interesting challenge, where it would be easier to allow an env var override
        os.environ['XKCD_PASSWORD'] = 'incorrect horse battery staple'

        # as illustrated here, we can override from an os env var, if needed
        assert config.get('XKCD_PASSWORD') == 'incorrect horse battery staple'

        # delete it and go back to the config value
        del os.environ['XKCD_PASSWORD']
        assert config.get('XKCD_PASSWORD') == 'correct horse battery staple'
