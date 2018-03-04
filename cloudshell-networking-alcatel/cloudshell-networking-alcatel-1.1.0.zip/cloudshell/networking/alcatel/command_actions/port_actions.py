import re

from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from cloudshell.networking.alcatel.command_templates import port_template


class PortActions(object):
    def __init__(self, cli_service, logger, port_name):
        """Port actions

        :param CliService cli_service: enable mode cli_service
        :param logger:
        :param str port_name:
        """

        self._cli_service = cli_service
        self._logger = logger
        self.port_name = self._get_port_name(port_name)

    def _get_port_name(self, port_name):
        """Get port name from port resource full address

        :param str port_name: port resource full address
            e.g. alcatel/Chassis 1/Module 1/SubModule 1/Port 1-1-14
        :return: port name (1/1/14)
        :rtype: str
        """

        if not port_name:
            err_msg = 'Failed to get port name.'
            self._logger.error(err_msg)
            raise Exception(self.__class__.__name__, err_msg)

        port = port_name.split('/')[-1]
        port = port.split(' ')[-1]
        port = port.replace('-', '/')
        self._logger.info('Interface name validation OK, port name - "{0}"'.format(port))

        return port

    def set_port_mode(self, qnq):
        """Set port mode

        :param bool qnq:
        """

        mode = 'hybrid' if qnq else 'network'
        CommandTemplateExecutor(
            self._cli_service,
            port_template.SET_PORT_MODE,
        ).execute_command(port=self.port_name, mode=mode)

    def set_port_encap_type(self, qnq):
        """Set port encap type

        :param bool qnq:
        """

        encap_type = 'qinq' if qnq else 'dot1q'
        CommandTemplateExecutor(
            self._cli_service,
            port_template.SET_PORT_ENCAP_TYPE,
        ).execute_command(port=self.port_name, encap_type=encap_type)

    def shutdown(self):
        CommandTemplateExecutor(
            self._cli_service,
            port_template.SHUTDOWN,
        ).execute_command(port=self.port_name)

    def no_shutdown(self):
        CommandTemplateExecutor(
            self._cli_service,
            port_template.NO_SHUTDOWN,
        ).execute_command(port=self.port_name)

    def is_qnq_on_port(self):
        output = CommandTemplateExecutor(
            self._cli_service,
            port_template.SHOW_PORT_ETHERNET,
        ).execute_command(port=self.port_name)

        return bool(re.search('Encap Type\s*: QinQ', output))
