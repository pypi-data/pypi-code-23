"""teapot.py provides an example Steno3D project of a teapot"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import loads

from numpy import array

from .base import BaseExample, exampleproperty
from ..point import Mesh0D, Point
from ..project import Project
from ..surface import Mesh2D, Surface


class Teapot(BaseExample):
    """Teapot example

    This module provides example data for a teapot.
    """

    @exampleproperty
    def filenames(self):
        return ['teapot.json']

    @exampleproperty
    def _data(self):
        """teapot data read from json"""
        if getattr(self, '__data', None) is None:
            json_file = Teapot.fetch_data(filename='teapot.json',
                                          download_if_missing=False,
                                          verbose=False)
            with open(json_file, 'r') as f:
                self.__data = loads(f.read())
        return self.__data

    @exampleproperty
    def vertices(self):
        """n x 3 numpy array of teapot vertices"""
        return array(self._data['vertices'])

    @exampleproperty
    def triangles(self):
        """n x 3 numpy array of teapot triangle vertex indices"""
        return array(self._data['triangles'])

    @classmethod
    def get_project(self):
        """return teapot project"""
        proj = Project(
            title='Teapot',
            description='Project with surface and points at vertices'
        )
        Point(
            project=proj,
            mesh=Mesh0D(
                vertices=self.vertices
            ),
            title='Teapot Vertex Points'
        )
        Surface(
            project=proj,
            mesh=Mesh2D(
                vertices=self.vertices,
                triangles=self.triangles
            ),
            title='Teapot Surface'
        )
        return proj
