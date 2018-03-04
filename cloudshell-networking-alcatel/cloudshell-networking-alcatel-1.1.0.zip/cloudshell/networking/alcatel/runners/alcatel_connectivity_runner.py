from cloudshell.devices.runners.connectivity_runner import ConnectivityRunner

from cloudshell.networking.alcatel.flows.alcatel_add_vlan_flow import AlcatelAddVlanFlow
from cloudshell.networking.alcatel.flows.alcatel_remove_vlan_flow import AlcatelRemoveVlanFlow


class AlcatelConnectivityRunner(ConnectivityRunner):

    @property
    def add_vlan_flow(self):
        return AlcatelAddVlanFlow(self.cli_handler, self._logger)

    @property
    def remove_vlan_flow(self):
        return AlcatelRemoveVlanFlow(self.cli_handler, self._logger)
