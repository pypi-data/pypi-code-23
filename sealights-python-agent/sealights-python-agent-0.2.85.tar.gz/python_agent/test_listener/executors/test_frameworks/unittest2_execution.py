import logging
import sys

from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

if sys.version_info >= (2, 7):
    from python_agent.test_listener.integrations.unittest_helper import main as unittest_main
else:
    from python_agent.test_listener.integrations.unittest_26_helper import main as unittest_main

log = logging.getLogger(__name__)


class Unittest2AgentExecution(AgentExecution):

    def __init__(self, config_data, labid, test_stage, args):
        super(Unittest2AgentExecution, self).__init__(config_data, labid, test_stage)
        self.args = args

    def execute(self):
        unittest_main(["unit2"] + list(self.args))
