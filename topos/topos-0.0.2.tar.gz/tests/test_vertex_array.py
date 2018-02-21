from pytest import raises
from hypothesis import given
import numpy as np


from topos.mesh import Coord
from topos.vertices import VertexArray


class TestInit(object):

    def test_no_args(self):

        verts = VertexArray()

        assert verts._data is None
        assert verts._coord == Coord.CARTESIAN

    def test_bad_verts(self):

        with raises(TypeError) as err:
            verts = VertexArray("String")

        assert 'array with shape (n, 3)' in str(err.value)

        with raises(TypeError) as err:
            verts = VertexArray(np.array([[2], [1], [3]]))

        assert 'array with shape (n, 3)' in str(err.value)

    def test_bad_coord(self):

        with raises(TypeError) as err:
            verts = VertexArray(coord="Polar")

        assert 'must be one of' in str(err.value)
