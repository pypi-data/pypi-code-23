# coding=utf-8

from pathlib import Path

import elib
from click.testing import CliRunner
from mockito import ANY, verify, when

import edlm.cli
import edlm.convert


def test_basic(runner: CliRunner):
    result = runner.invoke(edlm.cli.cli)
    assert result.exit_code == 0
    assert 'Usage: cli [OPTIONS] COMMAND [ARGS]...' in result.output


def test_debug(runner: CliRunner):
    when(elib.custom_logging).set_handler_level(...)
    when(edlm.cli.PANDOC).setup(...)
    when(edlm.cli.MIKTEX).setup(...)
    when(edlm.cli).make_pdf(...)
    runner.invoke(edlm.cli.cli, ['convert', 'pdf'])
    verify(edlm.cli.PANDOC).setup(...)
    verify(edlm.cli.MIKTEX).setup(...)
    verify(elib.custom_logging).set_handler_level('EDLM', 'ch', 'info')
    runner.invoke(edlm.cli.cli, ['--debug', 'convert', 'pdf'])
    verify(elib.custom_logging).set_handler_level('EDLM', 'ch', 'debug')


def test_make_pdf(runner: CliRunner):
    folder1 = Path('./folder1').absolute()
    folder2 = Path('./folder2').absolute()
    folder3 = Path('./folder3').absolute()
    folder1.mkdir()
    folder2.mkdir()
    folder3.mkdir()
    when(edlm.cli.PANDOC).setup(...)
    when(edlm.cli.MIKTEX).setup(...)
    when(edlm.cli).make_pdf(...)
    runner.invoke(edlm.cli.cli, ['convert', 'pdf', 'folder1', 'folder2', 'folder3'])
    verify(edlm.cli.PANDOC).setup(...)
    verify(edlm.cli.MIKTEX).setup(...)
    verify(edlm.cli).make_pdf(ANY, str(folder1))
    verify(edlm.cli).make_pdf(ANY, str(folder2))
    verify(edlm.cli).make_pdf(ANY, str(folder3))
