# coding=utf-8
"""
Pytest config
"""

import os
import sys

import pytest
from click.testing import CliRunner
from mockito import unstub


@pytest.fixture(scope='session')
def miktex_path():
    yield os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            'miktex',
        )
    )


@pytest.fixture()
def runner():
    runner_ = CliRunner()
    yield runner_


# noinspection PyUnusedLocal
def pytest_configure(config):
    """Setup"""
    assert config
    sys.called_from_test = True
    sys.path.append('.')


def pytest_unconfigure(config):
    """Tear down"""
    # noinspection PyUnresolvedReferences
    del sys.called_from_test
    assert config
    sys.path.remove('.')


@pytest.fixture(autouse=True)
def cleandir(request, tmpdir):
    """Provides a clean working dir"""
    if 'nocleandir' in request.keywords:
        yield
    else:
        current_dir = os.getcwd()
        os.chdir(str(tmpdir))
        yield os.getcwd()
        os.chdir(current_dir)


@pytest.fixture(autouse=True)
def _unstub():
    unstub()
    yield
    unstub()


@pytest.fixture(autouse=True)
def _reset_cache():
    from edlm.external_tools.base import _find_patool
    _find_patool.cache_clear()
    yield
    _find_patool.cache_clear()


@pytest.fixture(autouse=True)
def _setup_config():
    from edlm.config import CFG
    CFG.keep_temp_dir = False
    CFG.debug = False
    yield


def pytest_addoption(parser):
    """Add option for long tests"""
    parser.addoption("--long", action="store_true",
                     help="run long tests")


def pytest_runtest_setup(item):
    """Skip long tests"""
    long_marker = item.get_marker("long")
    if long_marker is not None and not item.config.getoption('long'):
        pytest.skip('skipping long tests')
