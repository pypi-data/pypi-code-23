from mock import patch

from cloudshell.networking.alcatel.runners.alcatel_configuration_runner import \
    AlcatelConfigurationRunner
from tests.networking.alcatel.base_test import CliEmulator, DEFAULT_PROMPT, BaseAlcatelTestCase


class TestRestoreConfig(BaseAlcatelTestCase):

    def _setUp(self, attrs=None):
        super(TestRestoreConfig, self)._setUp(attrs)
        self.runner = AlcatelConfigurationRunner(
            self.logger, self.resource_config, self.api, self.cli_handler)

    def setUp(self):
        super(TestRestoreConfig, self).setUp()
        self._setUp()

    def test_restore_startup_append(self):
        self.assertRaises(
            Exception,
            self.runner.restore,
            'ftp://test.url', 'startup', 'append')

    def test_restore_running_append(self):
        self.assertRaises(
            Exception,
            self.runner.restore,
            'ftp://test.url', 'running', 'append')

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_restore_startup_override(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        ftp = 'ftp://test.url'
        file_name = 'Alcatel-startup-200218-133900'
        emu = CliEmulator([
            [r'^show bof$',
             '{0} show bof\n'
             '===============================================================================\n'
             'BOF (Memory)\n'
             '===============================================================================\n'
             'primary-image      cf1:/images/TiMOS-8.0.R4\n'
             'primary-config     cf1:/config.cfg\n'
             '===============================================================================\n'
             '{0}'''.format(DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1} cf1:/{1}$'.format(ftp, file_name),
             'Copying file cf1:\{} ... OK\n1 file copied.\n{}'.format(file_name, DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1}\.sdx cf1:/{1}\.sdx$'.format(ftp, file_name),
             'Copying file cf1:\{}.sdx ... OK\n1 file copied.\n{}'.format(file_name, DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1}\.ndx cf1:/{1}\.ndx$'.format(ftp, file_name),
             'Copying file cf1:\{}.ndx ... OK\n1 file copied.\n{}'.format(file_name, DEFAULT_PROMPT),
             1],
            [r'^bof primary-config cf1:/{}$'.format(file_name),
             '{}'.format(DEFAULT_PROMPT),
             1],
            ['^bof save$',
             'Writing BOF to cf1:/bof.cfg ... OK\nCompleted.\n{}'.format(DEFAULT_PROMPT),
             1],
        ])
        recv_mock.side_effect = emu.receive_all
        send_mock.side_effect = emu.send_line

        path = '{}/{}'.format(ftp, file_name)
        self.runner.restore(path, 'startup', 'override')

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_restore_running_override(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        ftp = 'ftp://test.url'
        file_name = 'Alcatel-startup-200218-133900'
        emu = CliEmulator([
            [r'^show bof$',
             '''{0} show bof\n
             ===============================================================================\n
             BOF (Memory)\n
             ===============================================================================\n
             primary-image      cf1:/images/TiMOS-8.0.R4\n
             primary-config     cf1:/config.cfg\n
             ===============================================================================\n
             {0}'''.format(DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1} cf1:/{1}$'.format(ftp, file_name),
             'Copying file cf1:\{} ... OK\n1 file copied.\n{}'.format(file_name, DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1}\.sdx cf1:/{1}\.sdx$'.format(ftp, file_name),
             'Copying file cf1:\{}.sdx ... OK\n1 file copied.\n{}'.format(file_name, DEFAULT_PROMPT),
             1],
            [r'^file copy {0}/{1}\.ndx cf1:/{1}\.ndx$'.format(ftp, file_name),
             'Copying file cf1:\{}.ndx ... OK\n1 file copied.\n{}'.format(file_name, DEFAULT_PROMPT),
             1],
            [r'^bof primary-config cf1:/{}$'.format(file_name),
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^bof primary-config cf1:/config.cfg$',
             '{}'.format(DEFAULT_PROMPT),
             1],
            ['^bof save$',
             'Writing BOF to cf1:/bof.cfg ... OK\nCompleted.\n{}'.format(DEFAULT_PROMPT),
             2],
            ['^admin reboot now$',
             [Exception(),
              '{}'.format(DEFAULT_PROMPT)],
             2],  # it called one time, but next time doesn't called the send_line command
        ])
        recv_mock.side_effect = emu.receive_all
        send_mock.side_effect = emu.send_line

        path = '{}/{}'.format(ftp, file_name)
        self.runner.restore(path, 'running', 'override')

        emu.check_calls()
