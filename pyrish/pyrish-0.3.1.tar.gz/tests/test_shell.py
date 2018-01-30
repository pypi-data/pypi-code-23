from unittest import mock

import pytest

from pyrish.shell import run_shell
from pyrish.shell.exceptions import (
    CommandNotFoundError,
    UnexpectedShellError,
    MissingPermissionError
)


@mock.patch('pyrish.shell.subprocess')
def test_run_shell_succeed(subprocess):
    subprocess.getstatusoutput.return_value = (0, 'random result')
    output = run_shell('ls -a')
    assert output == 'random result'


@mock.patch('pyrish.shell.subprocess')
def test_run_shell_fails_silently(subprocess):
    subprocess.getstatusoutput.return_value = (1, 'command not found')
    output = run_shell('ipconf', silent=True)
    assert output is None


@pytest.mark.parametrize('cmd, code, exception', [
    ('ipconf', 127, CommandNotFoundError),
    ('cat /bin/junk', 1, UnexpectedShellError),
    ('grep -x lk', 2, UnexpectedShellError),
    ('/etc/hosts', 126, MissingPermissionError),
    ('/bin/kill $$', -15, UnexpectedShellError),
])
@mock.patch('pyrish.shell.subprocess')
def test_run_shell_fails_with_exception(subprocess, cmd, code, exception):
    subprocess.getstatusoutput.return_value = (code, 'random error message')
    with pytest.raises(exception) as e:
        run_shell(cmd)
        assert e.error == 'random error message'
        assert e.code == code
        assert e.cmd == cmd
