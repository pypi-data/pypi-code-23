from cloudshell.cli.command_template.command_template import CommandTemplate


SET_PORT_MODE = CommandTemplate(
    'configure port {port} ethernet mode {mode}',
    error_map={
        'A SAP exists on port': Exception('Can\'t change port mode')})
SET_PORT_ENCAP_TYPE = CommandTemplate('configure port {port} ethernet encap-type {encap_type}')

SHUTDOWN = CommandTemplate('configure port {port} shutdown')
NO_SHUTDOWN = CommandTemplate('configure port {port} no shutdown')

SHOW_PORT_ETHERNET = CommandTemplate('show port {port} ethernet')
