# coding=utf-8

import sys
from pathlib import Path

import elib._run
from elib.settings import ELIBSettings


def test_find_executable():
    python = elib._run.find_executable('python')
    assert elib._run.find_executable('python.exe') == python
    assert elib._run.find_executable('python', f'{sys.prefix}/Scripts') == python
    assert elib._run.find_executable('__sure__not__') is None


def test_context():
    assert elib._run.find_executable('__sure__not__') is None
    ELIBSettings.known_executables['__sure__not__.exe'] = 'ok'
    assert elib._run.find_executable('__sure__not__') == 'ok'


def test_paths():
    assert elib._run.find_executable('python')
    assert elib._run.find_executable('python', '.')
    ELIBSettings.known_executables = {}
    assert elib._run.find_executable('python', '.') is None


def test_immediate():
    Path('./test.exe').touch()
    assert elib._run.find_executable('test')
