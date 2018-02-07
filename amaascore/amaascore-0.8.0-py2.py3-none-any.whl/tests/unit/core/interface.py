from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
from datetime import datetime, timedelta
import logging.config
import unittest

from amaascore.core.interface import Interface

logging.config.dictConfig(DEFAULT_LOGGING)

logger = logging.getLogger(__name__)


class InterfaceTest(unittest.TestCase):

    def test_GenerateConfigFilename(self):
        # This isn't a great test since there are too many permutations to properly test
        interface = Interface(endpoint_type='DUMMY', endpoint='DUMMY', logger=logger)
        self.assertIsNotNone(interface.generate_config_filename())

    def test_MultipleSessionsShareLogin(self):
        interface1 = Interface(endpoint_type='DUMMY', endpoint='DUMMY', logger=logger)
        interface2 = Interface(endpoint_type='DUMMY', endpoint='DUMMY', logger=logger)
        self.assertEqual(interface1.session.last_authenticated, interface2.session.last_authenticated)

    def test_NeedsRefresh(self):
        interface1 = Interface(endpoint_type='DUMMY', endpoint='DUMMY', logger=logger)
        self.assertEqual(interface1.session.needs_refresh(), False)
        # Fake the last_authenticated timing
        interface1.session.last_authenticated = datetime.utcnow() - timedelta(hours=1)
        self.assertEqual(interface1.session.needs_refresh(), True)

    def test_ClientCognitoToken(self):
        interface1 = Interface(endpoint_type='DUMMY', endpoint='DUMMY', logger=logger, session_token='DUMMY_TOKEN')
        self.assertEqual(interface1.session.session.headers.get('Authorization'), 'DUMMY_TOKEN')

if __name__ == '__main__':
    unittest.main()
