"""rocket.py provides an example Steno3D project of rocket engine surface"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .base import BaseExample, exampleproperty
from ..project import Project
from ..surface import Mesh2D, Surface


class Rocket(BaseExample):
    """Class containing components of rocket engine surface project.

    Construct the project with Rocket.get_project()
    """

    @exampleproperty
    def filenames(self):
        """all rocket engine files"""
        return ['vertices.npz', 'triangles.npz', 'license.txt']

    @exampleproperty
    def vertices(self):
        """rocket engine vertex file"""
        return Rocket.fetch_data(filename='vertices.npz',
                                 download_if_missing=False,
                                 verbose=False)

    @exampleproperty
    def triangles(self):
        """rocket engine triangle  file"""
        return Rocket.fetch_data(filename='triangles.npz',
                                 download_if_missing=False,
                                 verbose=False)

    @classmethod
    def get_project(self):
        """return rocket engine surface project"""
        proj = Project(
            title='F-1 Rocket Engine',
            description='Engine used in the Saturn V. Model by Hlynkacg'
        )
        verts = np.load(Rocket.vertices)
        tris = np.load(Rocket.triangles)
        for arr_name in tris.files:
            Surface(
                project=proj,
                mesh=Mesh2D(
                    vertices=verts[arr_name],
                    triangles=tris[arr_name],
                ),
                title='Rocket Engine Surface: {}'.format(arr_name)
            )
        return proj
