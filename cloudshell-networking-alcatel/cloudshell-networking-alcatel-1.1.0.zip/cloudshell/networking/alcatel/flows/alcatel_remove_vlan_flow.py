from cloudshell.devices.flows.action_flows import RemoveVlanFlow

from cloudshell.networking.alcatel.command_actions.port_actions import PortActions
from cloudshell.networking.alcatel.command_actions.vlan_actions import VlanActions


class AlcatelRemoveVlanFlow(RemoveVlanFlow):

    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        """Remove configuration of VLAN on multiple ports or port-channels

        :param vlan_range: VLAN id
        :param port_name: full port name
        :param port_mode: mode which will be configured on port, trunk or access
        :param action_map:
        :param error_map:
        :rtype: str
        """

        if '-' in vlan_range:
            raise Exception('Doesn\'t support VLAN range')
        vlan_id = vlan_range  # doesn't support range

        self._logger.info("Remove Vlan {} configuration started".format(vlan_range))

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            port_actions = PortActions(enable_session, self._logger, port_name)
            port_name = port_actions.port_name
            qnq = port_actions.is_qnq_on_port()

            vlan_actions = VlanActions(enable_session, self._logger, port_name, vlan_id, qnq)
            vlan_actions.remove_sub_interface()

            if vlan_actions.is_configured_sub_interface():
                raise Exception(self.__class__.__name__,
                                "[FAIL] VLAN {} removing failed".format(vlan_range))

        self._logger.info("VLAN {} removing completed successfully".format(vlan_range))
        return "[ OK ] VLAN {} removing completed successfully".format(vlan_range)
