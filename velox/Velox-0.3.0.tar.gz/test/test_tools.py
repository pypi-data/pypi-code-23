import pytest
import pickle
import numpy as np

from velox import VeloxObject, register_object
from velox.tools import (fullname, import_from_qualified_name,
                         obtain_padding_bytes, obtain_qualified_name,
                         VELOX_NEW_FILE_SIGNATURE,
                         VELOX_NEW_FILE_EXTRAS_LENGTH)


def create_class(name, version='0.1.0', constraints=None):
    @register_object(
        registered_name=name,
        version=version,
        version_constraints=constraints
    )
    class _Model(VeloxObject):

        def __init__(self, o=None):
            super(_Model, self).__init__()
            self._o = o

        def _save(self, fileobject):
            pickle.dump(self._o, fileobject)

        @classmethod
        def _load(cls, fileobject):
            r = cls()
            setattr(r, '_o', pickle.load(fileobject))
            return r

        def obj(self):
            return self._o

    return _Model


def test_proper_fullname():
    x = np.random.normal(0, 1, (10, ))
    assert fullname(x) == 'numpy.ndarray'

    m = create_class('foo')()
    assert fullname(m) == 'test_tools._Model'


def test_import_from_qualified_name():
    clf = import_from_qualified_name('sklearn.linear_model.SGDRegressor')()
    assert clf

    from sklearn.linear_model import SGDRegressor
    assert isinstance(clf, SGDRegressor)


def test_obtain_padding_bytes():
    x = np.random.normal(0, 1, (10, ))

    b = obtain_padding_bytes(x).decode()

    assert len(b) == VELOX_NEW_FILE_EXTRAS_LENGTH
    assert VELOX_NEW_FILE_SIGNATURE in b
    assert obtain_qualified_name(b) == 'numpy.ndarray'
