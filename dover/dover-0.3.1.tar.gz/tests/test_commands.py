import os
from contextlib import contextmanager
from pathlib import Path
import pytest
from dover import commands
from dover.project import ConfigurationError
from dover.project import VersionMissMatchError 


@contextmanager
def new_cwd(new_dir):
    try:
        cwd = Path.cwd()
        os.chdir(str(new_dir))
        yield

    finally:
        os.chdir(str(cwd))


def test_command_no_config(tmpdir, capsys):
    with new_cwd(tmpdir):
        commands.version({})

    captured = capsys.readouterr()
    assert captured.out == "Dover found no configuration files!\n"


def test_command_version(files, capsys):

    with new_cwd(files.temp_dir):
        commands.version({})

    captured = capsys.readouterr()
    assert captured.out == "0.3.0\n"


def test_command_display(files, capsys):

    with new_cwd(files.temp_dir):
        commands.display({})

    captured = capsys.readouterr()
    assert captured.out == ("Current Version: 0.3.0\n"
                            "Files:\n"
                            "    setup.py    0005 (__version__ = '0.3.0') \n"
                            "    setup.cfg   0002 (version = 0.3.0)       \n"
                            "    newd/cli.py 0002 (__version__ = '0.3.0') \n"
                            "    README.md   0000 (#### newd app v0.3.0)  \n")


def create_args(**kwargs):
    return {
        '--major': kwargs.get('major'), 
        '--minor': kwargs.get('minor'), 
        '--patch': kwargs.get('patch'), 
        '--alpha': kwargs.get('alpha'),
        '--beta': kwargs.get('beta'),
        '--rc': kwargs.get('rc'), 
        '--no-list': kwargs.get('no_list'),
        '--apply': kwargs.get('apply'),
        '--debug': kwargs.get('debug')
    }


def test_command_missmatch_files(missmatch_files, capsys):

    with new_cwd(missmatch_files.temp_dir):
        commands.increment(create_args(major=True))
    
    captured = capsys.readouterr()
    assert captured.out == ("Not all file versions match:\n"
                            "\n"
                            "    setup.py    0.3.0 (__version__ = '0.3.0') \n"
                            "    setup.cfg   0.3.0 (version = 0.3.0)       \n"
                            "    newd/cli.py 6.6.6 (__version__ = '6.6.6') \n"
                            "    README.md   0.3.0 (#### newd app v0.3.0)  \n")


def test_command_increment_major_no_list(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(major=True, no_list=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     1.0.0\n")


def test_command_increment_major(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(major=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     1.0.0\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 1.0.0)\n"
                            "    setup.cfg   (0.3.0 -> 1.0.0)\n"
                            "    newd/cli.py (0.3.0 -> 1.0.0)\n"
                            "    README.md   (0.3.0 -> 1.0.0)\n")


def test_command_increment_minor(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(minor=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.4.0\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.4.0)\n"
                            "    setup.cfg   (0.3.0 -> 0.4.0)\n"
                            "    newd/cli.py (0.3.0 -> 0.4.0)\n"
                            "    README.md   (0.3.0 -> 0.4.0)\n")


def test_command_increment_patch(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(patch=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.3.1\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.3.1)\n"
                            "    setup.cfg   (0.3.0 -> 0.3.1)\n"
                            "    newd/cli.py (0.3.0 -> 0.3.1)\n"
                            "    README.md   (0.3.0 -> 0.3.1)\n")


def test_command_increment_alpha(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(alpha=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.3.0-alpha\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.3.0-alpha)\n"
                            "    setup.cfg   (0.3.0 -> 0.3.0-alpha)\n"
                            "    newd/cli.py (0.3.0 -> 0.3.0-alpha)\n"
                            "    README.md   (0.3.0 -> 0.3.0-alpha)\n")


def test_command_increment_beta(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(beta=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.3.0-beta\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.3.0-beta)\n"
                            "    setup.cfg   (0.3.0 -> 0.3.0-beta)\n"
                            "    newd/cli.py (0.3.0 -> 0.3.0-beta)\n"
                            "    README.md   (0.3.0 -> 0.3.0-beta)\n")


def test_command_increment_rc(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(rc=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.3.0-rc\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.3.0-rc)\n"
                            "    setup.cfg   (0.3.0 -> 0.3.0-rc)\n"
                            "    newd/cli.py (0.3.0 -> 0.3.0-rc)\n"
                            "    README.md   (0.3.0 -> 0.3.0-rc)\n")


def test_command_increment_major_alpha(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(major=True, alpha=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     1.0.0-alpha\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 1.0.0-alpha)\n"
                            "    setup.cfg   (0.3.0 -> 1.0.0-alpha)\n"
                            "    newd/cli.py (0.3.0 -> 1.0.0-alpha)\n"
                            "    README.md   (0.3.0 -> 1.0.0-alpha)\n")


def fetch_lines(pthobj):
    with pthobj.open(mode='r') as fh_:
        return fh_.readlines()


def test_command_increment_minor_apply(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment(create_args(minor=True, apply=True))

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.4.0\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.4.0)\n"
                            "    setup.cfg   (0.3.0 -> 0.4.0)\n"
                            "    newd/cli.py (0.3.0 -> 0.4.0)\n"
                            "    README.md   (0.3.0 -> 0.4.0)\n"
                            "Version updates applied.\n")

    assert '0.4.0' in fetch_lines(files.setup_py)[5]
    assert '0.4.0' in fetch_lines(files.setup_cfg)[2]
    assert '0.4.0' in fetch_lines(files.cli_py)[2]
    assert '0.4.0' in fetch_lines(files.readme)[0]
