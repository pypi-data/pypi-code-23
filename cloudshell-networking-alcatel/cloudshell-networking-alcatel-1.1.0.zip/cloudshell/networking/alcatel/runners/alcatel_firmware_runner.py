from cloudshell.devices.runners.firmware_runner import FirmwareRunner

from cloudshell.networking.alcatel.flows.alcatel_load_firmware_flow import AlcatelLoadFirmwareFlow


class AlcatelFirmwareRunner(FirmwareRunner):
    @property
    def load_firmware_flow(self):
        return AlcatelLoadFirmwareFlow(self.cli_handler, self._logger)
