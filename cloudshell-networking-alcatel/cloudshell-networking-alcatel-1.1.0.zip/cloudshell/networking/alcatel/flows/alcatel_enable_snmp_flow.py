from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters, \
    SNMPV2ReadParameters

from cloudshell.networking.alcatel.command_actions.enable_disable_snmp_actions \
    import EnableDisableSnmpV2Actions, EnableDisableSnmpV3Actions


class AlcatelEnableSnmpFlow(EnableSnmpFlow):
    DEFAULT_SNMP_VIEW = 'quali_snmp_view'
    DEFAULT_SNMP_GROUP = 'quali_snmp_group'
    SNMP_AUTH_MAP = {v: k for k, v in SNMPV3Parameters.AUTH_PROTOCOL_MAP.iteritems()}
    SNMP_PRIV_MAP = {v: k for k, v in SNMPV3Parameters.PRIV_PROTOCOL_MAP.iteritems()}
    NO_AUTH = 'No Authentication Protocol'
    NO_PRIV = 'No Privacy Protocol'
    ALCATEL_SNMP_AUTH_MAP = {'No Authentication Protocol': 'none', 'MD5': 'md5', 'SHA': 'sha'}
    ALCATEL_SNMP_PRIV_MAP = {'No Privacy Protocol': 'none', 'DES': 'des-key',
                             'AES-128': 'aes-128-cfb-key'}

    def execute_flow(self, snmp_param):
        if isinstance(snmp_param, SNMPV3Parameters):
            raise NotImplementedError('Doesn\'t support configuring SNMP V3')
        else:
            self._enable_snmp_v2(snmp_param)

    def _enable_snmp_v2(self, snmp_param):
        """Enable SNMP V2

        :param SNMPV2WriteParameters|SNMPV2ReadParameters snmp_param:
        """

        self._validate_snmp_v2_params(snmp_param)

        snmp_community = snmp_param.snmp_community

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_service:
            snmp_actions = EnableDisableSnmpV2Actions(enable_service, self._logger)
            snmp_actions.enable_snmp_server()

            if not snmp_actions.is_configured(snmp_community):
                access_mode = 'rw' if isinstance(snmp_param, SNMPV2WriteParameters) else 'r'
                snmp_actions.enable_snmp(snmp_community, access_mode)
            else:
                self._logger.debug('SNMP Community "{}" already configured'.format(snmp_community))
                return

            self._logger.info('Start verification of SNMP config')
            if not snmp_actions.is_configured(snmp_community):
                raise Exception(self.__class__.__name__,
                                'Failed to create SNMP community. Please check Logs for details')

    def _enable_snmp_v3(self, snmp_param):
        """Enable SNMP V3
        
        :param SNMPV3Parameters snmp_param:
        """

        auth_type = self.SNMP_AUTH_MAP.get(snmp_param.auth_protocol)
        priv_type = self.SNMP_PRIV_MAP.get(snmp_param.private_key_protocol)

        self._validate_snmp_v3_params(snmp_param, auth_type, priv_type)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as service:
            snmp_actions = EnableDisableSnmpV3Actions(service, self._logger)
            snmp_actions.enable_snmp_server()

            if snmp_actions.is_exists_user(snmp_param.snmp_user):
                self._logger.debug('SNMP User "{}" already exists'.format(snmp_param.snmp_user))
                return

            snmp_actions.enable_view(self.DEFAULT_SNMP_VIEW)
            snmp_actions.enable_group(
                self.DEFAULT_SNMP_VIEW,
                self.DEFAULT_SNMP_GROUP,
                self._get_security_level(auth_type, priv_type),
            )
            snmp_actions.enable_snmp_user(
                snmp_param.snmp_user,
                self.DEFAULT_SNMP_GROUP,
                self.ALCATEL_SNMP_AUTH_MAP[auth_type],
                snmp_param.snmp_password,
                self.ALCATEL_SNMP_PRIV_MAP[priv_type],
                snmp_param.private_key_protocol,
            )

            self._logger.info('Start verification of SNMP config')
            if not snmp_actions.is_exists_user(snmp_param.snmp_user):
                raise Exception(self.__class__.__name__,
                                'Failed to create SNMP user. Please check Logs for details')

    @staticmethod
    def _get_security_level(auth_type, priv_type):
        if auth_type == 'No Authentication Protocol':
            security_level = 'no-auth-no-privacy'
        elif auth_type != 'No Authentication Protocol' and priv_type == 'No Privacy Protocol':
            security_level = 'auth-no-privacy'
        else:
            security_level = 'privacy'

        return security_level

    def _validate_snmp_v2_params(self, snmp_param):
        if not snmp_param.snmp_community:
            message = 'SNMP community cannot be empty'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

    def _validate_snmp_v3_params(self, snmp_param, auth_type, priv_type):
        message = 'Failed to enable SNMP v3, {}'

        if not snmp_param.snmp_user:
            message = message.format('SNMP V3 User attribute cannot be empty')
        elif not snmp_param.auth_protocol:
            message = message.format('SNMP V3 Authentication Protocol attribute cannot be empty')
        elif not snmp_param.private_key_protocol:
            message = message.format('SNMP V3 Privacy Protocol attribute cannot be empty')
        elif priv_type not in self.ALCATEL_SNMP_PRIV_MAP.keys():
            protocols = ', '.join(self.ALCATEL_SNMP_PRIV_MAP.keys())
            message = message.format(
                'device support only {} SNMP V3 Privacy Protocols'.format(protocols)
            )
        elif auth_type == self.NO_AUTH and priv_type != self.NO_PRIV:
            message = message.format(
                'you can\'t set SNMP V3 Privacy Protocol "{}" and '
                'SNMP V3 Authentication Protocol "{}"'.format(priv_type, auth_type)
            )
        elif auth_type != self.NO_AUTH and not snmp_param.snmp_password:
            message = message.format('SNMP V3 Password attribute cannot be empty')
        elif priv_type != self.NO_PRIV and not snmp_param.snmp_private_key:
            message = message.format('SNMP V3 Private Key attribute cannot be empty')
        else:
            return

        self._logger.error(message)
        raise Exception(self.__class__.__name__, message)
