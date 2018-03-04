from cloudshell.devices.runners.configuration_runner import ConfigurationRunner

from cloudshell.networking.alcatel.flows.alcatel_restore_flow import AlcatelRestoreFlow
from cloudshell.networking.alcatel.flows.alcatel_save_flow import AlcatelSaveFlow


class AlcatelConfigurationRunner(ConfigurationRunner):
    @property
    def restore_flow(self):
        return AlcatelRestoreFlow(self.cli_handler, self._logger)

    @property
    def save_flow(self):
        return AlcatelSaveFlow(self.cli_handler, self._logger)

    @property
    def file_system(self):
        return 'cf1:'
