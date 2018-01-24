# -*- coding: utf-8 -*-

import mock
import pytest

from s4 import cli


# TODO: Should catch KeyboardExceptions and raise them again
class TestMain(object):

    @mock.patch('argparse.ArgumentParser.print_help')
    def test_no_arguments_prints_help(self, print_help):
        cli.main([])
        assert print_help.call_count == 1

    @pytest.mark.parametrize(['loglevel'], [('INFO', ), ('DEBUG', )])
    @mock.patch('logging.basicConfig')
    def test_timestamps(self, basicConfig, loglevel):
        cli.main(['--timestamps', '--log-level', loglevel, 'version'])
        assert basicConfig.call_args[1]['format'].startswith('%(asctime)s: ')

    @mock.patch('logging.basicConfig')
    def test_debug_loglevel(self, basicConfig):
        cli.main(['--log-level=DEBUG', 'version'])
        assert basicConfig.call_args[1]['format'].startswith('%(levelname)s:%(module)s')
        assert basicConfig.call_args[1]['level'] == 'DEBUG'

    def test_version_command(self, capsys):
        cli.main(['version'])
        out, err = capsys.readouterr()
        assert out == '{}\n'.format(cli.VERSION)

    @mock.patch('s4.cli.LsCommand')
    def test_ls_command(self, LsCommand):
        cli.main(['ls', 'foo'])
        assert LsCommand.call_count == 1

    @mock.patch('s4.cli.DaemonCommand')
    def test_daemon_command(self, DaemonCommand):
        cli.main(['daemon'])
        assert DaemonCommand.call_count == 1

    @mock.patch('s4.cli.SyncCommand')
    def test_sync_command(self, SyncCommand):
        cli.main(['sync', 'foo'])
        assert SyncCommand.call_count == 1

    @mock.patch('s4.cli.EditCommand')
    def test_edit_command(self, EditCommand):
        cli.main(['edit', 'foo'])
        assert EditCommand.call_count == 1

    @mock.patch('s4.cli.TargetsCommand')
    def test_targets_command(self, TargetsCommand):
        cli.main(['targets'])
        assert TargetsCommand.call_count == 1

    @mock.patch('s4.cli.RmCommand')
    def test_rm_command(self, RmCommand):
        cli.main(['rm', 'foo'])
        assert RmCommand.call_count == 1

    @mock.patch('s4.cli.AddCommand')
    def test_add_command(self, AddCommand):
        cli.main(['add'])
        assert AddCommand.call_count == 1
