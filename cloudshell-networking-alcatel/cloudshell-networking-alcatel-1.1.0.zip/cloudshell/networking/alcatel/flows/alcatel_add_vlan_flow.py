from cloudshell.devices.flows.action_flows import AddVlanFlow

from cloudshell.networking.alcatel.command_actions.port_actions import PortActions
from cloudshell.networking.alcatel.command_actions.vlan_actions import VlanActions


class AlcatelAddVlanFlow(AddVlanFlow):

    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        """Configures VLAN on multiple ports or port-channels

        :param vlan_range: VLAN id
        :param port_mode: mode which will be configured on port, trunk or access
        :param port_name: full port name
        :param qnq:
        :param c_tag:
        :rtype: str
        """

        if '-' in vlan_range:
            raise Exception('Doesn\'t support VLAN range')
        vlan_id = vlan_range  # doesn't support range

        self._logger.info("Add VLAN {} configuration started".format(vlan_id))

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            port_actions = PortActions(enable_session, self._logger, port_name)
            port_actions.shutdown()
            port_actions.set_port_mode(qnq)
            port_actions.set_port_encap_type(qnq)
            port_actions.no_shutdown()
            port_name = port_actions.port_name

            vlan_actions = VlanActions(enable_session, self._logger, port_name, vlan_id, qnq)
            vlan_actions.remove_all_sub_interfaces()
            vlan_actions.create_sub_interface()

            if not vlan_actions.is_configured_sub_interface():
                raise Exception(self.__class__.__name__,
                                '[FAIL] VLAN {} configuration failed'.format(vlan_id))

        self._logger.info('VLAN {} configuration completed successfully'.format(vlan_id))
        return '[ OK ] VLAN {} configuration completed successfully'.format(vlan_id)
