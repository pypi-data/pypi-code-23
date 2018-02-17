import numpy as np
from topos import Mesh


class TestInit(object):

    def test_init_no_args(self):
        mesh = Mesh()

        assert mesh._name is None
        assert mesh._vertices is None
        assert mesh._faces is None
        assert (mesh._position == np.array([0., 0., 0.])).all()
