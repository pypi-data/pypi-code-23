import re

from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from cloudshell.networking.alcatel.command_templates import vlan_template


class VlanActions(object):
    def __init__(self, cli_service, logger, port_name, vlan_id, qnq):
        """Service actions

        :param CliService cli_service: enable mode cli_service
        :param logger:
        :param str port_name:
        :param str vlan_id:
        :param bool qnq:
        """

        self._cli_service = cli_service
        self._logger = logger
        self._port_name = port_name
        self._vlan_id = vlan_id
        self._qnq = qnq
        self.if_name = 'p{}:{}{}'.format(port_name, vlan_id, '.*' if qnq else '')

    def _get_interfaces_with_vlan(self):
        """Getting names of sub interfaces with used VLAN on the port

        :return: list of sub interface names for the port with VLANs
        :rtype: list
        """

        output = CommandTemplateExecutor(
            self._cli_service,
            vlan_template.SHOW_SUB_INTERFACES,
        ).execute_command()

        pattern = r'^(\S+).+?{}:\d+(?:\.\*)?$'.format(self._port_name)

        return re.findall(pattern, output, re.MULTILINE)

    def remove_all_sub_interfaces(self):
        """Remove all sub interfaces"""

        for if_name in self._get_interfaces_with_vlan():
            CommandTemplateExecutor(
                self._cli_service,
                vlan_template.SHUTDOWN_SUB_INTERFACE,
            ).execute_command(if_name=if_name)
            CommandTemplateExecutor(
                self._cli_service,
                vlan_template.REMOVE_SUB_INTERFACE,
            ).execute_command(if_name=if_name)

    def remove_sub_interface(self):
        """Remove sub interface"""

        CommandTemplateExecutor(
            self._cli_service,
            vlan_template.SHUTDOWN_SUB_INTERFACE,
        ).execute_command(if_name=self.if_name)
        CommandTemplateExecutor(
            self._cli_service,
            vlan_template.REMOVE_SUB_INTERFACE,
        ).execute_command(if_name=self.if_name)

    def create_sub_interface(self):
        """Create router interface for the port with VLAN"""

        kwargs = {'port_name': self._port_name, 'vlan_id': self._vlan_id, 'if_name': self.if_name}
        if self._qnq:
            kwargs['qnq'] = ''

        CommandTemplateExecutor(
            self._cli_service,
            vlan_template.CREATE_SUB_INTERFACE,
        ).execute_command(**kwargs)

    def is_configured_sub_interface(self):
        """Check that router interface is configured"""

        output = CommandTemplateExecutor(
            self._cli_service,
            vlan_template.SHOW_SUB_INTERFACES,
        ).execute_command()

        pattern = r'^{}.+?{}:{}{}$'.format(
            self.if_name,
            self._port_name,
            self._vlan_id,
            '.*' if self._qnq else '',
        )

        return bool(re.search(pattern, output, re.MULTILINE))
