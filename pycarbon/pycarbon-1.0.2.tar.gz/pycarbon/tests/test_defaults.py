import os
import unittest

from configuration import Configuration


class TestDefaults(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
        config_dir = os.path.join(project_root, 'config')
        os.environ['CONFIG_DIR'] = config_dir

    def test_default_constructor(self):
        config = Configuration()
        assert config.directory == os.environ['CONFIG_DIR']
        assert config.environment == 'development'
        assert 'config.yml' in config.files

    def test_get(self):
        config = Configuration()

        # load a value using the default environment
        assert config.get('foo') == 'dev-value'

        # load a value from specific environments
        assert config.get('foo', environment='staging') == 'staging-value'
        assert config.get('foo', environment='production') == 'production-value'

    def test_get_overrides(self):
        config = Configuration()

        # set in localhost.yml
        assert config.get('demo.localhost-override', environment='production') == 'some-localhost-default'

        # set in secrets.yml
        assert config.get('demo.api-key', environment='production') == 'production-secret'

    def test_get_using_delimiters(self):
        config = Configuration()

        assert config.get('demo.setting') == 'dev-value'
        assert config.get('demo:setting') == 'dev-value'
        assert config.get('demo/setting') == 'dev-value'
