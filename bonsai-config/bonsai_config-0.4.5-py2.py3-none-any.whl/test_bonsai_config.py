"""
This file contains unit tests for bonsai config library.
"""
import os
import tempfile
from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from six.moves.configparser import ConfigParser

from bonsai_config import BonsaiConfig


class TestBrainConfig(TestCase):

    def setUp(self):
        self.temp_path = os.path.join(tempfile.gettempdir(), 'test-bonsai')
        patcher = patch('bonsai_config.bonsai_config.CONFIG_FILE',
                        new=self.temp_path)

        self.addCleanup(patcher.stop)
        patcher.start()

    def tearDown(self):
        os.remove(self.temp_path)

    def test_url_pieces(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'HOST', 'local.bons.ai')
        cp.set('DEFAULT', 'PORT', '12345')
        cp.set('DEFAULT', 'USESSL', 'False')
        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig()
        self.assertEqual('http://local.bons.ai:12345', bc.brain_api_url())

    def test_url(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'URL', 'https://local.bons.ai:3456')
        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig()
        self.assertEqual('https://local.bons.ai:3456', bc.brain_api_url())

    def test_wss(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'URL', 'https://local.bons.ai:3456')
        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig()
        self.assertEqual('wss://local.bons.ai:3456', bc.brain_websocket_url())

    def test_section(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'USERNAME', 'bonsai')
        cp.set('DEFAULT', 'PROFILE', 'public')
        cp.add_section('public')
        cp.set('public', 'USERNAME', 'override')

        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig()
        self.assertEqual('override', bc.username())

    def test_fallback(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'USERNAME', 'bonsai')
        cp.set('DEFAULT', 'PROFILE', 'public')
        cp.add_section('public')
        cp.set('public', 'OTHER', 'value')

        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig()
        self.assertEqual('bonsai', bc.username())

    def test_profile(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'USERNAME', 'bonsai')
        cp.set('DEFAULT', 'HOST', 'local.bons.ai')

        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig(section='test')
        bc.update(HOST='override')
        self.assertEqual('override', bc._host())
        self.assertEqual('bonsai', bc.username())

        bc.update(Profile='DEFAULT')
        self.assertEqual('local.bons.ai', bc._host())

    def test_check_section_exists(self):
        cp = ConfigParser()
        cp.set('DEFAULT', 'USERNAME', 'bonsai')

        with open(self.temp_path, 'w') as f:
            cp.write(f)

        bc = BonsaiConfig(section='DEFAULT')
        self.assertEqual(True, bc.check_section_exists('DEFAULT'))
        self.assertEqual(False, bc.check_section_exists('FOO'))

        bc.update(Profile='FOO')
        self.assertEqual(True, bc.check_section_exists('FOO'))
