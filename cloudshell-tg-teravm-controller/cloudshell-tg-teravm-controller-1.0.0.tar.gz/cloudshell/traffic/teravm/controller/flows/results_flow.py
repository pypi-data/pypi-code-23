import tempfile

from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from scp import SCPClient

from cloudshell.traffic.teravm.cli import ctrl_command_templates
from cloudshell.traffic.teravm.controller import constants


class TeraVMGetResultsFlow(object):
    def __init__(self, cli_handler, quali_api_client, reservation_id):
        """

        :param traffic.teravm.cli.ctrl_handler.TeraVMControllerCliHandler cli_handler:
        :param traffic.teravm.quali_rest_api_helper.QualiAPIHelper quali_api_client:
        :param str reservation_id:
        """
        self._cli_handler = cli_handler
        self._quali_api_client = quali_api_client
        self._reservation_id = reservation_id

    def execute(self, test_group_name, user):
        """

        :param str test_group_name:
        :param str user:
        :return:
        """
        results_file = constants.TEST_RESULTS_FILE.format(user)

        with self._cli_handler.get_cli_service(self._cli_handler.cli_mode) as cli_session:
            command = CommandTemplateExecutor(cli_service=cli_session,
                                              command_template=ctrl_command_templates.SAVE_RESULTS)

            command.execute_command(test_group_name=test_group_name, destination_file=results_file, user=user)

        with self._cli_handler.get_cli_service(self._cli_handler.default_mode) as session:
            scp = SCPClient(session.session._handler.get_transport())

            tmp_file_path = tempfile.mktemp()
            scp.get(results_file, tmp_file_path)

            with open(tmp_file_path) as tmp_results_file:
                self._quali_api_client.upload_file(self._reservation_id,
                                                   file_name=constants.CS_TEST_RESULTS_ATTACHMENTS_FILE,
                                                   file_stream=tmp_results_file)
