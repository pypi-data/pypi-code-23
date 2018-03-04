from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from cloudshell.traffic.teravm.cli import ctrl_command_templates


class TeraVMCleanupFlow(object):
    def __init__(self, cli_handler):
        """

        :param traffic.teravm.cli.ctrl_handler.TeraVMControllerCliHandler cli_handler:
        """
        self._cli_handler = cli_handler

    def execute(self, test_group_name, user):
        """

        :param str test_group_name:
        :param str user:
        :return:
        """
        with self._cli_handler.get_cli_service(self._cli_handler.cli_mode) as session:

            command = CommandTemplateExecutor(cli_service=session,
                                              command_template=ctrl_command_templates.STOP_TEST_GROUP)

            try:
                command.execute_command(test_group_name=test_group_name, user=user)
            except Exception:
                pass

            command = CommandTemplateExecutor(cli_service=session,
                                              command_template=ctrl_command_templates.DELETE_TEST_GROUP)

            try:
                command.execute_command(test_group_name=test_group_name, user=user)
            except Exception:
                pass
