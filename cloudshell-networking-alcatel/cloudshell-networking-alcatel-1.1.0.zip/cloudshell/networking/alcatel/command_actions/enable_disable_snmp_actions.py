import re

from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from cloudshell.networking.alcatel.command_templates import enable_disable_snmp


class EnableDisableSnmpV2Actions(object):
    def __init__(self, cli_service, logger):
        """Enable Disable Snmp actions

        :param CliService cli_service: enable mode cli service
        :param logger:
        """

        self._cli_service = cli_service
        self._logger = logger

    def enable_snmp_server(self):
        """Enable SNMP server"""

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_SNMP_SERVER,
        ).execute_command()

    def is_configured(self, snmp_community):
        """Check snmp community is configured

        :param str snmp_community:
        :return: True or False
        :rtype: bool
        """

        output = self._cli_service.send_command('configure system security snmp community \t')
        snmp_community = '"{}"'.format(snmp_community)
        return snmp_community in output

    def enable_snmp(self, snmp_community, access_mode):
        """Enable snmp on the device

        :param snmp_community: community string
        :param access_mode: r or rw
        """

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_SNMPV2,
        ).execute_command(snmp_community=snmp_community, access_mode=access_mode)

    def disable_snmp(self, snmp_community):
        """Disable SNMP

        :param snmp_community: community string
        """
        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.DISABLE_SNMPV2,
        ).execute_command(snmp_community=snmp_community)


class EnableDisableSnmpV3Actions(object):
    def __init__(self, cli_service, logger):
        """Enable Disable Snmp actions

        :param CliService cli_service: enable mode cli service
        :param logger:
        """

        self._cli_service = cli_service
        self._logger = logger

    def enable_snmp_server(self):
        """Enable SNMP server"""
        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_SNMP_SERVER,
        ).execute_command()

    def is_exists_user(self, user):
        """Check user is exists

        :param str user: user name
        :return: True or False
        :rtype: bool
        """

        output = CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SHOW_USERS,
        ).execute_command()

        return bool(re.search(r'^{}\s'.format(user), output, re.MULTILINE))

    def enable_view(self, view):
        """Enable SNMP view

        :param str view: snmp view
        """

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_VIEW,
        ).execute_command(view=view)

    def disable_view(self, view):
        """Disable SNMP view

        :param str view: snmp view
        """

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.DISABLE_VIEW,
        ).execute_command(view=view)

    def enable_group(self, view, group, security_level):
        """Enable SNMP group

        :param str view: snmp view
        :param str group: snmp group
        :param str security_level: no-auth-no-privacy or auth-no-privacy or privacy
        """

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_GROUP,
        ).execute_command(view=view, group=group, security_level=security_level)

    def disable_group(self, group):
        """Disable SNMP group

        :param str group: snmp group
        """

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.DISABLE_GROUP,
        ).execute_command(group=group)

    def enable_snmp_user(self, user, group, auth_type, auth_key, priv_type, priv_key):
        """Enable snmp user

        :param str user: user name
        :param str group: snmp group
        :param str auth_type: authentication type none or md5 or sha
        :param str auth_key: password
        :param str priv_type: privacy type none or des-key or aes-128-cfb-key
        :param str priv_key: privacy key
        """

        if auth_type == 'none':
            auth_key = priv_type = priv_key = None
        if priv_type == 'none':
            priv_key = None

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_USER_ACCESS,
        ).execute_command(user=user)

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_USER_SNMP_AUTH,
        ).execute_command(user=user, auth_type=auth_type, auth_key=auth_key,
                          priv_type=priv_type, priv_key=priv_key)

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_USER_SNMP_GROUP,
        ).execute_command(user=user, group=group)

    def disable_snmp_user(self, user):
        """Enable snmp user

        :param str user: user name
        """

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.DISABLE_USER,
        ).execute_command(user=user)
