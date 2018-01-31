"""
.. module:: exchange_helpers
    :platform: Unix, Windows
    :synopsis: CAD exchange and interoperability module for NURBS-Python package

.. moduleauthor:: Onur Rauf Bingol <orbingol@gmail.com>

"""

from . import exchange_helpers as exh
from . import BSpline, NURBS


# Saves B-Spline and NURBS surfaces as Wavefront OBJ files
def save_obj(surface=None, file_name='', vertex_spacing=2):
    if not file_name:
        raise ValueError("File name field is required")

    if not isinstance(surface, BSpline.Surface):
        raise ValueError("Input is not a surface")

    try:
        with open(file_name, 'w') as fp:
            vertices, triangles = exh.make_obj_triangles(surface.surfpts,
                                                         int((1.0 / surface.delta) + 1), int((1.0 / surface.delta) + 1),
                                                         vertex_spacing)

            # # Evaluate face normals
            # uv_list = exh.make_obj_face_normals_uv(surface.delta, vertex_spacing)

            # Write vertices
            for vert_row in vertices:
                for vert in vert_row:
                    line = "v " + str(vert.x) + " " + str(vert.y) + " " + str(vert.z) + "\n"
                    fp.write(line)

            # Write vertex normals
            for vert_row in vertices:
                for vert in vert_row:
                    sn = surface.normal(vert.uv[0], vert.uv[1], True)
                    line = "vn " + str(sn[1][0]) + " " + str(sn[1][1]) + " " + str(sn[1][2]) + "\n"
                    fp.write(line)

            # Write faces
            for t in triangles:
                vl = t.vertex_ids
                line = "f " + str(vl[0]) + " " + str(vl[1]) + " " + str(vl[2]) + "\n"
                fp.write(line)
    except IOError:
        print("Cannot open " + str(file_name) + " for writing")
