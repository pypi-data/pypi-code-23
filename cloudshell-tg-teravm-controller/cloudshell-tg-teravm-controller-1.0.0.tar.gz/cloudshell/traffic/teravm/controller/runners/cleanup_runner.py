from cloudshell.traffic.teravm.cli.ctrl_handler import TeraVMControllerCliHandler

from cloudshell.traffic.teravm.controller.flows.cleanup_flow import TeraVMCleanupFlow
from cloudshell.traffic.teravm.controller.constants import TEST_GROUP_NAME


class TeraVMCleanupRunner(object):
    def __init__(self, cli, cs_api, resource_config, logger):
        """

        :param cloudshell.cli.cli.CLI cli: CLI object
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_api: cloudshell API object
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param logging.Logger logger:
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
    def cleanup_flow(self):
        """

        :return:
        """
        return TeraVMCleanupFlow(cli_handler=self.cli_handler)

    def cleanup_reservation(self):
        """

        :return:
        """
        return self.cleanup_flow.execute(test_group_name=TEST_GROUP_NAME, user=self._resource_config.test_user)
