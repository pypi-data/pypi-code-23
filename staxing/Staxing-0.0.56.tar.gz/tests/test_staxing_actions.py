"""Staxing test files - Actions."""

import time
import unittest

from random import randint
from selenium import webdriver
from selenium.webdriver.chrome import options
from staxing.actions import Actions

__version__ = '1.0.1'


class TestStaxingActions(unittest.TestCase):
    """Staxing case tests for the ActionChain sleep."""

    def setUp(self):
        """Pretest settings."""
        option_set = options.Options()
        option_set.add_argument('disable-infobars')
        option_set.add_argument('disable-geolocation')
        option_set.add_argument('headless')
        option_set.add_experimental_option(
            'prefs', {
                'credentials_enable_service': False,
                'profile': {
                    'password_manager_enabled': False
                }
            }
        )
        self.driver = webdriver.Chrome(chrome_options=option_set)
        self.action_chain = Actions(self.driver)

    def tearDown(self):
        """Test destructor."""
        try:
            self.action_chain.__del__()
            self.driver.__del__()
        except Exception:
            pass

    def test_actions_wait_within_two_percent_accuracy_100(self):
        """Test ActionChain wait time is accurate."""
        sleep_length = randint(3, 8) / 1.0
        start_time = time.time()
        self.action_chain.wait(sleep_length).perform()
        end_time = time.time()
        duration = end_time - start_time
        assert(duration >= sleep_length * 0.98), \
            'Sleep shorter than expected: %s < %s' % \
            (duration, sleep_length * 0.98)
        assert(duration <= sleep_length * 1.02), \
            'Sleep longer than expected: %s > %s' % \
            (duration, sleep_length * 1.02)
