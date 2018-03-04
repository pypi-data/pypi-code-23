from cloudshell.cli.command_template.command_template import CommandTemplate

SHOW_SUB_INTERFACES = CommandTemplate('show router interface')

SHUTDOWN_SUB_INTERFACE = CommandTemplate('configure router interface {if_name} shutdown')
REMOVE_SUB_INTERFACE = CommandTemplate('configure router no interface {if_name}')

CREATE_SUB_INTERFACE = CommandTemplate(
    'configure router interface {if_name} port {port_name}:{vlan_id}[.*{qnq}]')
