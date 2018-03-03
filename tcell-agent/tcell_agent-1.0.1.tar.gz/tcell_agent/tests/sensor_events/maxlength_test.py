import json
import unittest

from tcell_agent.sensor_events.server_agent_packages import ServerAgentPackagesEvent
from tcell_agent.api import SetEncoder


class MaxLengthTest(unittest.TestCase):
    def test_package_event_create(self):
        sape = ServerAgentPackagesEvent()
        sape.add_package("test_package", "t" * 400)
        x = json.loads(json.dumps(sape, cls=SetEncoder))
        self.assertEqual(x["packages"][0]["v"], "t" * 256)
