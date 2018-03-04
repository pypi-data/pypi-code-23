import re

from mock import patch

from cloudshell.networking.alcatel.flows.alcatel_load_firmware_flow import AlcatelLoadFirmwareFlow
from cloudshell.networking.alcatel.runners.alcatel_firmware_runner import AlcatelFirmwareRunner
from tests.networking.alcatel.base_test import BaseAlcatelTestCase, DEFAULT_PROMPT, CliEmulator


class TestLoadFirmware(BaseAlcatelTestCase):

    def _setUp(self, attrs=None):
        super(TestLoadFirmware, self)._setUp(attrs)
        self.runner = AlcatelFirmwareRunner(self.logger, self.cli_handler)

    def setUp(self):
        super(TestLoadFirmware, self).setUp()
        self._setUp()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_load_firmware(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        ftp = 'ftp://test.url'
        file_name = 'both.tim'

        emu = CliEmulator([
            [r'^file md {}$'.format(AlcatelLoadFirmwareFlow.FOLDER_PATH),
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1} {2}{1}$'.format(
                *map(re.escape, (ftp, file_name, AlcatelLoadFirmwareFlow.FOLDER_PATH))),
                'Copying file cf1:\config.cfg ... OK\n1 file copied.\n{}'.format(DEFAULT_PROMPT),
                1],
            [r'^bof primary-image {}$'.format(re.escape(AlcatelLoadFirmwareFlow.FOLDER_PATH)),
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^bof save$',
             'Writing BOF to cf1:/bof.cfg ... OK\nCompleted.\n{}'.format(DEFAULT_PROMPT),
             1],
            [r'^admin reboot upgrade now$',
             [Exception(),
              '{}'.format(DEFAULT_PROMPT)],
             2],  # it called one time, but next time doesn't called send_line command
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        path = '{}/{}'.format(ftp, file_name)
        self.runner.load_firmware(path)

        emu.check_calls()
