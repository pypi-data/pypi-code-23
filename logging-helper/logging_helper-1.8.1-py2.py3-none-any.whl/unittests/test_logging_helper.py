# encoding: utf-8

import unittest
import logging_helper
from logging_helper import _metadata
from testfixtures import LogCapture

logging = logging_helper.setup_logging(logger_name=u'TESTING HELPER',
                                       level=logging_helper.DEBUG,
                                       log_to_file=True)


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.lc = LogCapture()

    def tearDown(self):
        self.lc.uninstall()

    # Instantiation
    def test_version(self):
        self.assertEqual(logging_helper.__version__, _metadata.__version__, u'Version is incorrect')

    @unittest.skip(u'Test not refactored yet after adhoc transfer!')
    def test_console_set_level(self):

        logging.debug(u'Test log message 1')
        logging.lh_set_console_level(logging_helper.INFO)
        logging.debug(u'Test log message 2')  # This message should not display
        logging.lh_set_console_level(logging_helper.DEBUG)
        logging.debug(u'Test log message 3')

        self.lc.check(
            ('TESTING HELPER', 'DEBUG', 'Test log message 1'),
            ('TESTING HELPER', 'DEBUG', 'Test log message 3')
        )


if __name__ == u'__main__':
    unittest.main()
