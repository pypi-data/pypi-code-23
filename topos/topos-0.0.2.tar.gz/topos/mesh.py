from enum import Enum
import numpy as np


class Coord(Enum):
    CARTESIAN = 1
    CYLINDRICAL = 2


class Mesh(object):

    def __init__(self, name=None, vertices=None, faces=None, coord=None):

        if name is not None and not isinstance(name, (str,)):
                raise TypeError('Name property must be a string!')

        if vertices is not None:

            if not isinstance(vertices, (np.ndarray,)):
                raise TypeError('Vertices must be a numpy array with shape (n, 3)')

            vert_shape = vertices.shape

            if len(vert_shape) != 2 or vert_shape[1] != 3:
                raise TypeError('Vertices must be a numpy array with shape (n, 3)')

        if faces is not None:

            if not isinstance(faces, (np.ndarray)):
                raise TypeError('Faces must be a numpy array with shape (n, 4)')

            face_shape = faces.shape

            if len(face_shape) != 2 or face_shape[1] != 4:
                raise TypeError('Faces must be a numpy array with shape (n, 4)')

        self._name = name
        self._vertices = vertices
        self._faces = faces
        self._coord = Coord.CARTESIAN if coord is None else coord

    @property
    def name(self):
        return "" if self._name is None else self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, (str,)):
            raise TypeError("Name property must be a string!")

        self._name = value

    @property
    def faces(self):
        return self._faces

    @property
    def num_faces(self):
        if self._faces is None:
            return 0
        else:
            return self._faces.shape[0]

    @property
    def vertices(self):
            return self._vertices

    @property
    def num_vertices(self):
        if self._vertices is None:
            return 0
        else:
            return self._vertices.shape[0]

    def __repr__(self):
        s = "Mesh:\t\t{}\n".format(self.name)
        s += "Vertices:\t{}\n".format(self.num_vertices)
        s += "Faces:\t\t{}\n".format(self.num_faces)
        return s

    def save(self, filename):
        with open(filename, 'w') as f:

            # Write the object's name
            f.write("o {}\n".format(self._name))

            # Write all the vertices
            for vert in self.vertices:
                f.write("v {} {} {}\n".format(*vert))

            # Finally all the faces
            for face in self.faces:
                face_str = "f " + " ".join(str(f) for f in face) + "\n"
                f.write(face_str)
