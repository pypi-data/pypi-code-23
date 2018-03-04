from cloudshell.traffic.teravm.cli.ctrl_handler import TeraVMControllerCliHandler

from cloudshell.traffic.teravm.controller.constants import TEST_GROUP_NAME
from cloudshell.traffic.teravm.controller.flows.start_tests_flow import TeraVMStartTestsFlow
from cloudshell.traffic.teravm.controller.flows.stop_tests_flow import TeraVMStopTestsFlow


class TeraVMTestsRunner(object):
    def __init__(self, cli, cs_api, resource_config, logger):
        """

        :param cloudshell.cli.cli.CLI cli: CLI object
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_api: cloudshell API object
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param logging.Logger logger:
        :return:
        """
        self._cli = cli
        self._cs_api = cs_api
        self._resource_config = resource_config
        self._logger = logger

    @property
    def cli_handler(self):
        """

        :return:
        """
        return TeraVMControllerCliHandler(cli=self._cli,
                                          resource_config=self._resource_config,
                                          logger=self._logger,
                                          api=self._cs_api)

    @property
    def start_tests_flow(self):
        """

        :return:
        """
        return TeraVMStartTestsFlow(cli_handler=self.cli_handler)

    @property
    def stop_tests_flow(self):
        """

        :return:
        """
        return TeraVMStopTestsFlow(cli_handler=self.cli_handler)

    def start_tests(self):
        """

        :return:
        """
        return self.start_tests_flow.execute(test_group_name=TEST_GROUP_NAME, user=self._resource_config.test_user)

    def stop_tests(self):
        """

        :return:
        """
        return self.stop_tests_flow.execute(test_group_name=TEST_GROUP_NAME, user=self._resource_config.test_user)
