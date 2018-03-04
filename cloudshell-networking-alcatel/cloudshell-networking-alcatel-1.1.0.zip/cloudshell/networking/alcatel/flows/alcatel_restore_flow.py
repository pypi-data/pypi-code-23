from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow
from cloudshell.devices.networking_utils import UrlParser

from cloudshell.networking.alcatel.command_actions.system_actions import SystemActions


class AlcatelRestoreFlow(RestoreConfigurationFlow):
    DEFAULT_FILESYSTEM = 'cf1:/'

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
        """ Execute flow which restore selected file to the provided destination

        :param str path: the path to the configuration file, including the configuration file name
        :param str restore_method: the restore method to use when restoring the configuration file,
            append and override
        :param str configuration_type: the configuration type to restore, startup or running
        :param str vrf_management_name: Virtual Routing and Forwarding Name
        """

        if restore_method == 'append':
            msg = 'Restore method "append" not supported for the device'
            self._logger.error(msg)
            raise Exception(msg)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            dst = self._get_dst_path(path)
            system_action = SystemActions(enable_session, self._logger)
            old_primary_config_path = system_action.get_primary_config_path()

            for ext in ('', '.sdx', '.ndx'):
                system_action.copy(path + ext, dst + ext)

            system_action.change_primary_conf(dst)
            system_action.save_bof()

            if configuration_type == 'running':
                system_action.reboot()
                system_action.change_primary_conf(old_primary_config_path)
                system_action.save_bof()

    def _get_dst_path(self, path):
        file_name = UrlParser.parse_url(path).get(UrlParser.FILENAME)
        return self.DEFAULT_FILESYSTEM + file_name
