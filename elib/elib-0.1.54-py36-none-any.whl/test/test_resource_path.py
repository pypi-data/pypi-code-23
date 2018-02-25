# coding=utf-8
import sys
from pathlib import Path

import pytest
from mockito import verifyStubbedInvocationsAreUsed, when

import elib

HERE = Path('.').absolute()


def test_from_dev():
    assert elib.resource_path.get_resource_path(HERE.joinpath('elib'), 'run.py').exists()


def test_from_sys():
    setattr(sys, '_MEIPASS', str(HERE))
    assert elib.resource_path.get_resource_path('elib', 'elib/run.py').exists()


def test_from_package():
    when(elib.resource_path)._get_from_package('elib', Path('run.py')).thenReturn(Path(HERE, 'elib/run.py'))
    assert elib.resource_path.get_resource_path('elib', 'run.py').exists()
    verifyStubbedInvocationsAreUsed()


def test_not_found():
    with pytest.raises(FileNotFoundError):
        elib.resource_path.get_resource_path('elib', 'nope')
