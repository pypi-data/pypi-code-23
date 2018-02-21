import numpy as np
from math import pi


def planar_vertices(N):
    """
    Generate a grid of vertices in the X-Y Plane on
    :math:`[0, 1] \times [0, 1]` at the given resolution
    N
    """
    # Generate a grid of x-y values at the desired resolution
    xs = np.linspace(0, 1, N)
    XS, YS = np.meshgrid(xs, xs)

    # Reshape the grids to be one long array
    XS.shape = (N*N,)
    YS.shape = (N*N,)
    zeros = np.zeros(XS.shape)

    # Return the vertices all at z=0
    return np.dstack([XS, YS, zeros])


def cylindrical_vertices(N_theta, N_z):
    """
    Generate vertices in the shape of a cylinder
    coordinates are in cylindrical coordinates
    in the format (t, z, r)
    """

    ts = np.linspace(0, 2*pi, N_theta)
    zs = np.linspace(0, 1, N_z)

    TS, ZS = np.meshgrid(ts, zs)
    TS.shape = (N_theta * N_z,)
    ZS.shape = (N_theta * N_z,)
    ones = np.full(ZS.shape, 1.)

    return np.dstack([TS, ZS, ones])[0]


def cylindrical_faces(N_theta, N_z, close_loop=True):
    """
    Generate the face definitions for an object of cylindrical geometry
    optionally closing the loop
    """
    faces = []

    for j in range(0, N_z - 1):

            # Here I am using the fact that python promotes True/False to
            # 1/0 respectively when used in arithmetic to calculate the range
            for i in range(1, N_theta + (close_loop * 1)):

                # To get the normals pointing in the right direction we need
                # to define the corners in anti-clockwise order. So we will
                # # do it as follows:
                #      Lower left -> Lower right -> Upper right -> Upper left
                lower_left = j * N_theta + i
                lower_right = j*N_theta + i + 1
                upper_right = (j + 1) * N_theta + i + 1
                upper_left = (j + 1) * N_theta + i

                # Only the 'right hand' values could be problematic when closing
                # the loop
                if lower_right >= (j+1) * N_theta:
                    lower_right -= N_theta - 1

                if upper_right >= (j+2) * N_theta:
                    upper_right -= N_theta - 1

                # Add the face to the mesh
                faces.append((lower_left, lower_right, upper_right, upper_left))

    return np.array(faces)


def planar_faces(N):
    """
    Generate the face definitions for a planar grid of size N vertices
    by N vertices. To get the normals facing the right direction the elements
    of each face reference the vertex indices in the following order:

    4        <- 3
    *-----------*
    |           |
    |           |
    |           | ^
    |           | |
    *-----------* 2
    1 ->

    Parameters
    ----------
    N: int
        The number of vertices to include in the side of the mesh

    Returns
    -------
    faces: numpy.ndarray
        A numpy array of shape :math:`((N-1)^2, 4)` representing the faces
        of the mesh
    """

    # TODO: Is there a more "numpy" way to do this?
    faces = []
    for j in range(0, N - 1):
        for i in range(1, N):

            lower_left = i + (j * N)
            lower_right = (i + 1) + (j * N)
            upper_right = (i + 1) + ((j + 1) * N)
            upper_left = i + ((j + 1) * N)

            faces.append([lower_left, lower_right, upper_right, upper_left])

    return np.array(faces)
