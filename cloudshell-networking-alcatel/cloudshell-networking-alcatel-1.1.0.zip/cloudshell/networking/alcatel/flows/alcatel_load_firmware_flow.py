from cloudshell.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.devices.networking_utils import UrlParser

from cloudshell.networking.alcatel.command_actions.system_actions import SystemActions


class AlcatelLoadFirmwareFlow(LoadFirmwareFlow):
    FOLDER_PATH = 'cf1:/quali_firmware/'

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        """

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            dst = self._get_dst_path(path)

            system_action = SystemActions(enable_session, self._logger)
            system_action.create_folder(self.FOLDER_PATH)
            system_action.copy(path, dst)
            system_action.change_primary_image(self.FOLDER_PATH)
            system_action.save_bof()
            system_action.reboot(upgrade=True)

    def _get_dst_path(self, path):
        file_name = UrlParser.parse_url(path).get(UrlParser.FILENAME)
        return self.FOLDER_PATH + file_name
