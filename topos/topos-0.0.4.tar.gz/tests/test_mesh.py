from pytest import raises
from hypothesis import given
from hypothesis.strategies import text
from .strategies import vertices, faces


import numpy as np
from topos import Mesh
from topos.mesh import Coord


class TestInit(object):

    def test_no_args(self):
        mesh = Mesh()

        assert mesh._name is None
        assert mesh._vertices is None
        assert mesh._faces is None
        assert mesh._coord == Coord.CARTESIAN

    @given(name=text())
    def test_name(self, name):
        mesh = Mesh(name=name)

        assert mesh._name == name

        with raises(TypeError) as err:
            mesh = Mesh(name=2)

        assert 'must be a string' in str(err.value)

    @given(vertices=vertices())
    def test_vertices(self, vertices):

        mesh = Mesh(vertices=vertices)
        assert (mesh._vertices == vertices).all()

    def test_vertices_bad_values(self):

        with raises(TypeError) as err:
            mesh = Mesh(vertices=[4, 5, 6])

        assert 'array with shape (n, 3)' in str(err.value)

        verts = np.array([[1, 2, 3, 4],
                          [5, 6, 7, 8]])

        with raises(TypeError) as err:
            mesh = Mesh(vertices=verts)

        assert 'array with shape (n, 3)' in str(err.value)

    @given(faces=faces())
    def test_faces(self, faces):
        mesh = Mesh(faces=faces)
        assert (mesh.faces == faces).all()

    def test_faces_bad_values(self):

        with raises(TypeError) as err:
            mesh = Mesh(faces=[2, 3, 4])

        assert 'array with shape (n, 4)' in str(err.value)

        faces = np.array([[[1, 2, 3, 4],
                            [2, 3, 4, 5]]])

        with raises(TypeError) as err:
            mesh = Mesh(faces=faces)

        assert 'array with shape (n, 4)' in str(err.value)



class TestProperties(object):


    @given(name=text())
    def test_name_property(self, name):
        mesh = Mesh()

        # By default no name should be the empty string
        assert mesh.name == ""

        # And of course setting the name should work
        mesh.name = name
        assert mesh.name == name

    def test_name_property_bad_value(self):
        mesh = Mesh("square")

        # Names should only be a string
        with raises(TypeError) as err:
            mesh.name = 2

        assert "must be a string" in str(err.value)

        # Name should be unchanged
        assert mesh.name == "square"
