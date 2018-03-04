#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.snmp_handler import SnmpHandler

from cloudshell.networking.alcatel.flows.alcatel_disable_snmp_flow import AlcatelDisableSnmpFlow
from cloudshell.networking.alcatel.flows.alcatel_enable_snmp_flow import AlcatelEnableSnmpFlow


class AlcatelSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(AlcatelSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return AlcatelEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return AlcatelDisableSnmpFlow(self.cli_handler, self._logger)
