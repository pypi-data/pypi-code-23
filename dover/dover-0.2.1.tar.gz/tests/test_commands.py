import os
from contextlib import contextmanager
from pathlib import Path
from dover import commands


@contextmanager
def new_cwd(new_dir):
    cwd = Path.cwd()
    os.chdir(str(new_dir))
    yield
    os.chdir(str(cwd))


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


def test_command_increment(files, capsys):

    with new_cwd(files.temp_dir):
        commands.increment({'--major': None, '--minor': True, '--patch': None, '--apply': False})

    captured = capsys.readouterr()

    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     0.4.0\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 0.4.0)\n"
                            "    setup.cfg   (0.3.0 -> 0.4.0)\n"
                            "    newd/cli.py (0.3.0 -> 0.4.0)\n"
                            "    README.md   (0.3.0 -> 0.4.0)\n")
