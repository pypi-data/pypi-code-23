import os

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow

from cloudshell.networking.alcatel.command_actions.system_actions import SystemActions


class AlcatelSaveFlow(SaveConfigurationFlow):
    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """Execute flow which save selected file to the provided destination

        :param folder_path: destination path where file will be saved
        :param configuration_type: running or startup
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            system_action = SystemActions(enable_session, self._logger)

            if configuration_type == 'running':
                system_action.copy_running_config(folder_path)
            else:
                config_path = system_action.get_startup_config_path()
                system_action.copy(config_path, folder_path)

                file_name, old_ext = os.path.splitext(config_path)
                for ext in ('.sdx', '.ndx'):
                    system_action.copy(file_name + ext, folder_path + ext)
