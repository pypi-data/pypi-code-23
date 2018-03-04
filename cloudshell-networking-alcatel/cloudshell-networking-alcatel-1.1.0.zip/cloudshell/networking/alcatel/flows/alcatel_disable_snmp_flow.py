from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters, \
    SNMPV2ReadParameters

from cloudshell.networking.alcatel.command_actions.enable_disable_snmp_actions \
    import EnableDisableSnmpV2Actions, EnableDisableSnmpV3Actions


class AlcatelDisableSnmpFlow(DisableSnmpFlow):
    DEFAULT_SNMP_VIEW = 'quali_snmp_view'
    DEFAULT_SNMP_GROUP = 'quali_snmp_group'

    def execute_flow(self, snmp_param=None):
        if isinstance(snmp_param, SNMPV3Parameters):
            raise NotImplementedError('Doesn\'t support configuring SNMP v3')
        else:
            self._disable_snmp_v2(snmp_param)

    def _disable_snmp_v2(self, snmp_param):
        """Disable SNMP V3

        :param SNMPV2WriteParameters|SNMPV2ReadParameters snmp_param:
        """

        snmp_community = snmp_param.snmp_community

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as service:
            snmp_actions = EnableDisableSnmpV2Actions(service, self._logger)

            self._logger.debug('Start Disable SNMP')
            snmp_actions.disable_snmp(snmp_community)

            self._logger.info('Start verification of SNMP config')
            if snmp_actions.is_configured(snmp_community):
                raise Exception(self.__class__.__name__,
                                'Failed to remove SNMP community. Please check Logs for details')

    def _disable_snmp_v3(self, snmp_param):
        """Disable SNMP V3

        :param SNMPV3Parameters snmp_param:
        """

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as service:
            snmp_actions = EnableDisableSnmpV3Actions(service, self._logger)

            if snmp_actions.is_exists_user(snmp_param.snmp_user):
                self._logger.debug('Start Disable SNMP')
                snmp_actions.disable_view(self.DEFAULT_SNMP_VIEW)
                snmp_actions.disable_group(self.DEFAULT_SNMP_GROUP)
                snmp_actions.disable_snmp_user(snmp_param.snmp_user)

            self._logger.info('Start verification of SNMP config')
            if snmp_actions.is_exists_user(snmp_param.snmp_user):
                raise Exception(self.__class__.__name__,
                                "Failed to remove SNMP user. Please check Logs for details")
