""" Test supporting module
"""

from fslutils.supporting import Bunch, read_file

import pytest


def test_read_file():
    with open(__file__, 'rt') as fobj:
        contents = fobj.read()
    assert contents == read_file(__file__)


def test_bunch():
    foo = dict(foo=1, bar=2, baz=3)
    bfoo = Bunch(foo)
    assert bfoo.foo == 1
    assert bfoo.bar == 2
    assert bfoo.baz == 3
    bfoo.bunch_update(dict(spam='eggs', bar=99))
    assert bfoo.foo == 1
    assert bfoo.bar == 99
    assert bfoo.baz == 3
    assert bfoo.spam == 'eggs'
    # Dunder key ignored
    bfoo.bunch_update(dict(__newspam='green eggs', bar=199))
    assert bfoo.foo == 1
    assert bfoo.bar == 199
    assert bfoo.baz == 3
    assert bfoo.spam == 'eggs'
    with pytest.raises(ValueError):
        Bunch(dict(bunch_foo='something'))
    with pytest.raises(ValueError):
        bfoo.bunch_update(dict(bunch_foo='something'))
