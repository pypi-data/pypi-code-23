import gocept.loginuser.bcrypt
import gocept.testing.patch
import pytest


@pytest.yield_fixture(scope='module', autouse=True)
def patches():
    """Patch bcrypt WORK_FACTOR to speed up tests."""
    patch = gocept.testing.patch.Patches()
    patch.set(gocept.loginuser.bcrypt, 'WORK_FACTOR', 4)
    yield
    patch.reset()
