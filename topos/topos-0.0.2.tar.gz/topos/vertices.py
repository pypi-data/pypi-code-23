import numpy as np
from .mesh import Coord


class VertexArray(object):


    def __init__(self, verts=None, coord=None):

        if verts is not None:

            if not isinstance(verts, (np.ndarray,)):
                raise TypeError('Vertices must be a numpy array with shape (n, 3)')

            shape = verts.shape

            if len(shape) != 2 or shape[1] != 3:
                raise TypeError('Vertices must be a numpy array with shape (n, 3)')

        if coord is not None:

            if not isinstance(coord, (Coord,)):
                message = "Coordinate System must be one of "
                message += ", ".join(c.name for c in iter(Coord))
                raise TypeError(message)

        self._data = verts
        self._coord = Coord.CARTESIAN if coord is None else coord
