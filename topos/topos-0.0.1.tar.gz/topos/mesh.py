import numpy as np


class Mesh(object):

    def __init__(self, name=None, vertices=None, faces=None):
        self._name = name
        self._vertices = vertices
        self._faces = faces
        self._position = np.array([0, 0, 0])

    @property
    def name(self):
        if self._name is None:
            return ""
        else:
            return self._name

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        if pos.shape != (3,):
            raise TypeError("Position must be a numpy array of form [x, y, z]")

        self._position = pos

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
        return self._vertices + self._position

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
