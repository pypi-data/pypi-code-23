from .mesh import Mesh, Coord
from .generators import planar_faces, planar_vertices,\
        cylindrical_faces, cylindrical_vertices


class Plane(Mesh):

    def __init__(self, N=4, size=1.0):

        verts = size * planar_vertices(N)
        faces = planar_faces(N)
        super().__init__(name="Plane", vertices=verts, faces=faces)


class Cylinder(Mesh):

    def __init__(self, N_theta=8, N_z=6):

        verts = cylindrical_vertices(N_theta, N_z)
        faces = cylindrical_faces(N_theta, N_z)

        super().__init__(name="Cylinder", vertices=verts, faces=faces,
                         coord=Coord.CYLINDRICAL)
