from restclients_core.tests.dao_implementation.test_backend import TDAO
from unittest import TestCase, skipUnless
from commonconf import override_settings
import datetime


class TestTimingLog(TestCase):

    @skipUnless(hasattr(TestCase, 'assertLogs'), 'Python < 3.4')
    @override_settings(RESTCLIENTS_TIMING_START=(datetime.datetime.now() +
                       datetime.timedelta(1)).isoformat(),
                       RESTCLIENTS_TIMING_END=(datetime.datetime.now() +
                       datetime.timedelta(2)).isoformat(),
                       RESTCLIENTS_TIMING_LOG_ENABLED=True,
                       RESTCLIENTS_TIMING_LOG_RATE=1.0)
    def test_dont_log_date_range(self):
        with self.assertRaises(AssertionError):
            with self.assertLogs('restclients_core.dao', level='INFO') as cm:
                response = TDAO().getURL('/ok')
                self.assertEquals(len(cm.output), 0)

    @skipUnless(hasattr(TestCase, 'assertLogs'), 'Python < 3.4')
    @override_settings(RESTCLIENTS_TIMING_START=(datetime.datetime.now() -
                       datetime.timedelta(1)).isoformat(),
                       RESTCLIENTS_TIMING_END=(datetime.datetime.now() +
                       datetime.timedelta(2)).isoformat(),
                       RESTCLIENTS_TIMING_LOG_ENABLED=True,
                       RESTCLIENTS_TIMING_LOG_RATE=1.0)
    def test_log_date_range(self):
        with self.assertLogs('restclients_core.dao', level='INFO') as cm:
            response = TDAO().getURL('/ok')
            self.assertEquals(len(cm.output), 1)

    @skipUnless(hasattr(TestCase, 'assertLogs'), 'Python < 3.4')
    @override_settings(RESTCLIENTS_TIMING_LOG_ENABLED=False,
                       RESTCLIENTS_TIMING_LOG_RATE=1.0,
                       RESTCLIENTS_BACKEND_TEST_TIMING_LOG_ENABLED=True)
    def test_per_service_config(self):
        with self.assertLogs('restclients_core.dao', level='INFO') as cm:
            response = TDAO().getURL('/ok')
            self.assertEquals(len(cm.output), 1)
