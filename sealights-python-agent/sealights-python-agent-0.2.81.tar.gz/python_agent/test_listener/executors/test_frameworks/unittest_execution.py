import logging
import sys

from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

if sys.version_info >= (2, 7):
    from python_agent.test_listener.integrations.unittest_helper import main as unittest_main
else:
    from python_agent.test_listener.integrations.unittest_26_helper import main as unittest_main

log = logging.getLogger(__name__)


class UnittestAgentExecution(AgentExecution):

    def __init__(self, config_data, labid, test_stage, is_junit, output, args):
        super(UnittestAgentExecution, self).__init__(config_data, labid, test_stage)
        self.args = args
        self.is_junit = is_junit
        self.output = output

    def execute(self):
        unittest_main(["unittest"] + list(self.args), is_junit=self.is_junit, output=self.output)
