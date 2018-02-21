import numpy as np
from .mesh import Mesh


class Translate(object):
    """
    Translate an object by [dx, dy, dz]
    """

    def __init__(self, dx, dy, dz):

        self._offset = np.array([dx, dy, dz])

    def __rrshift__(self, mesh):

        vs = mesh._vertices
        vs += self._offset

        return Mesh(mesh.name, vertices=vs, faces=mesh.faces,
                    coord=mesh._coord)


class Scale(object):
    """
    Scale either in all directions or a specified axis
    """
    def __init__(self, all=1.):
        self._all = all

    def __rrshift__(self, mesh):

        vs = mesh._vertices
        vs *= self._all

        return Mesh(mesh.name, vertices=vs, faces=mesh.faces,
                    coord=mesh._coord)


def translate(dx=0., dy=0., dz=0.):
    return Translate(dx, dy, dz)


def scale(x):
    return Scale(all=x)
