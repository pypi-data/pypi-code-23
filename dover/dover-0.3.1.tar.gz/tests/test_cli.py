import sys
import pytest
from dover import cli


def test_cli_no_args(files, capsys, monkeypatch):

    monkeypatch.chdir(files.temp_dir)
    monkeypatch.setattr(sys, 'argv', [''])
    cli.main()

    captured = capsys.readouterr()
    assert captured.out == "0.3.0\n"


def test_cli_list(files, capsys, monkeypatch):

    monkeypatch.chdir(files.temp_dir)
    monkeypatch.setattr(sys, 'argv', ['', '--list'])
    cli.main()

    captured = capsys.readouterr()
    assert captured.out == ("Current Version: 0.3.0\n"
                            "Files:\n"
                            "    setup.py    0005 (__version__ = '0.3.0') \n"
                            "    setup.cfg   0002 (version = 0.3.0)       \n"
                            "    newd/cli.py 0002 (__version__ = '0.3.0') \n"
                            "    README.md   0000 (#### newd app v0.3.0)  \n")


def test_cli_increment(files, capsys, monkeypatch):

    monkeypatch.chdir(files.temp_dir)
    monkeypatch.setattr(sys, 'argv', ['', 'increment', '--major'])
    cli.main()

    captured = capsys.readouterr()
    assert captured.out == ("Current Version: 0.3.0\n"
                            "New Version:     1.0.0\n"
                            "Files:\n"
                            "    setup.py    (0.3.0 -> 1.0.0)\n"
                            "    setup.cfg   (0.3.0 -> 1.0.0)\n"
                            "    newd/cli.py (0.3.0 -> 1.0.0)\n"
                            "    README.md   (0.3.0 -> 1.0.0)\n")
