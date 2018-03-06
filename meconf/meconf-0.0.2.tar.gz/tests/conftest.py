import os
from pathlib import Path

import pytest


@pytest.fixture
def pathlib_tmpdir(tmpdir):
    return Path(tmpdir)


@pytest.fixture(autouse=True)
def environ():
    old_environ = os.environ.copy()
    yield os.environ
    os.environ = old_environ
