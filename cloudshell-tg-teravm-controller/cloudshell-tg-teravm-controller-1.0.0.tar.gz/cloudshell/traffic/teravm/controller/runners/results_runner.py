from cloudshell.traffic.teravm.cli.ctrl_handler import TeraVMControllerCliHandler

from cloudshell.traffic.teravm.controller.flows.results_flow import TeraVMGetResultsFlow
from cloudshell.traffic.teravm.controller.constants import TEST_GROUP_NAME


class TeraVMResultsRunner(object):
    def __init__(self, cli, cs_api, resource_config, reservation_id, quali_api_client, logger):
        """

        :param cloudshell.cli.cli.CLI cli: CLI object
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_api: cloudshell API object
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param traffic.teravm.quali_rest_api_helper.QualiAPIHelper quali_api_client:
        :param logging.Logger logger:
        """
        self._cli = cli
        self._cs_api = cs_api
        self._resource_config = resource_config
        self._reservation_id = reservation_id
        self._quali_api_client = quali_api_client
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
    def get_results_flow(self):
        """

        :return:
        """
        return TeraVMGetResultsFlow(cli_handler=self.cli_handler,
                                    quali_api_client=self._quali_api_client,
                                    reservation_id=self._reservation_id)

    def get_results(self):
        """"""
        return self.get_results_flow.execute(test_group_name=TEST_GROUP_NAME, user=self._resource_config.test_user)
