import logging

from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

log = logging.getLogger(__name__)


class PytestAgentExecution(AgentExecution):

    def __init__(self, config_data, labid, test_stage, args):
        super(PytestAgentExecution, self).__init__(config_data, labid, test_stage)
        self.args = args

    def execute(self):
        try:
            args = list(self.args)
            from pytest import main as pytest_main
            from python_agent.test_listener.integrations import pytest_helper

            pytest_main(args=args, plugins=[pytest_helper.SealightsPlugin()])
        except ImportError as e:
            log.exception("Failed Importing pytest. Error: %s" % str(e))
