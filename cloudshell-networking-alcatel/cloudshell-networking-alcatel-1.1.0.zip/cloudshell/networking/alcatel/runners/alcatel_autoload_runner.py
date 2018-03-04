#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner

from cloudshell.networking.alcatel.flows.alcatel_autoload_flow import AlcatelSnmpAutoloadFlow


class AlcatelAutoloadRunner(AutoloadRunner):
    def __init__(self, resource_config, logger, snmp_handler):
        super(AlcatelAutoloadRunner, self).__init__(resource_config)
        self._logger = logger
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return AlcatelSnmpAutoloadFlow(self.snmp_handler, self._logger)
