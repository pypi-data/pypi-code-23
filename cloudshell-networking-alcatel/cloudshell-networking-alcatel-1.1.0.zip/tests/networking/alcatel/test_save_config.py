from mock import patch

from cloudshell.networking.alcatel.runners.alcatel_configuration_runner import \
    AlcatelConfigurationRunner
from tests.networking.alcatel.base_test import CliEmulator, DEFAULT_PROMPT, BaseAlcatelTestCase


class TestSaveConfig(BaseAlcatelTestCase):

    def _setUp(self, attrs=None):
        attributes = {
            'Backup Location': 'folder',
        }
        attributes.update(attrs or {})

        super(TestSaveConfig, self)._setUp(attributes)
        self.runner = AlcatelConfigurationRunner(
            self.logger, self.resource_config, self.api, self.cli_handler)

    def setUp(self):
        super(TestSaveConfig, self).setUp()
        self._setUp()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_startup(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        ftp = 'ftp://test.url'
        file_pattern = r'Alcatel-startup-\d+-\d+'
        emu = CliEmulator([
            ['^show system information$',
             '{0} show system information\n\n'
             '===============================================================================\n'
             'System Information\n'
             '===============================================================================\n'
             'System Name            : test\n'
             'System Type            : 7210 SAS-M-1\n'
             'System Version         : B-8.0.R4\n\n'
             'BOF Source             : cf1:\n'
             'Image Source           : primary\n'
             'Config Source          : primary\n'
             'Last Booted Config File: cf1:\config.cfg\n'
             '{0}'''.format(DEFAULT_PROMPT), 1],
            [r'^file copy cf1:\\config.cfg {}/{}$'.format(ftp, file_pattern),
             'Copying file cf1:\config.cfg ... OK\n1 file copied.\n{}'.format(DEFAULT_PROMPT),
             1],
            [r'^file copy cf1:\\config\.sdx {}/{}\.sdx$'.format(ftp, file_pattern),
             'Copying file cf1:\config.cfg ... OK\n1 file copied.\n{}'.format(DEFAULT_PROMPT),
             1],
            [r'^file copy cf1:\\config\.ndx {}/{}\.ndx$'.format(ftp, file_pattern),
             'Copying file cf1:\config.cfg ... OK\n1 file copied.\n{}'.format(DEFAULT_PROMPT),
             1],
        ])
        recv_mock.side_effect = emu.receive_all
        send_mock.side_effect = emu.send_line

        self.runner.save(ftp, 'startup')

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_running(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        ftp = 'ftp://test.url'
        file_pattern = r'Alcatel-running-\d+-\d+'
        emu = CliEmulator([
            [r'^admin save {}/{}$'.format(ftp, file_pattern),
             'Completed.\n{}'.format(DEFAULT_PROMPT),
             1],
        ])
        recv_mock.side_effect = emu.receive_all
        send_mock.side_effect = emu.send_line

        self.runner.save(ftp, 'running')

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_to_default_location(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        file_pattern = r'Alcatel-running-\d+-\d+'
        emu = CliEmulator([
            [r'^admin save {}//folder/{}'.format(self.runner.file_system, file_pattern),
             'Completed.\n{}'.format(DEFAULT_PROMPT),
             1],
        ])
        recv_mock.side_effect = emu.receive_all
        send_mock.side_effect = emu.send_line

        self.runner.save(configuration_type='running')

        emu.check_calls()
