from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import numpy as np

from .base import BaseExample, exampleproperty
from ..data import DataArray
from ..project import Project
from ..surface import Mesh2D, Mesh2DGrid, Surface
from ..texture import Texture2DImage


class Topography(BaseExample):
    """Topography example

    This module provides example data for a topography surface.
    """

    @exampleproperty
    def filenames(self):
        return ['topo_grid.json', 'topo_tris.json', 'topo.png']

    @exampleproperty
    def gridfile(self):
        return Topography.fetch_data(filename='topo_grid.json',
                                     download_if_missing=False,
                                     verbose=False)

    @exampleproperty
    def trifile(self):
        return Topography.fetch_data(filename='topo_tris.json',
                                     download_if_missing=False,
                                     verbose=False)

    @exampleproperty
    def griddata(self):
        """topography data from json"""
        with open(Topography.gridfile, 'r') as f:
            topo = json.load(f)
        return topo

    @exampleproperty
    def tridata(self):
        """topography data from json"""
        with open(Topography.trifile, 'r') as f:
            topo = json.load(f)
        return topo

    @exampleproperty
    def topo_image(self):
        """surface image"""
        return Topography.fetch_data(filename='topo.png',
                                     download_if_missing=False,
                                     verbose=False)

    @exampleproperty
    def topo_image_orientation(self):
        """surface image O, U, and V"""
        return dict(
            O=[443200., 491750, 0],
            U=[4425., 0, 0],
            V=[0., 3690, 0]
        )

    @classmethod
    def get_project(self):
        """return topography project"""
        elev_n = np.array(Topography.tridata['vertices'])[:, 2]
        elev_cc = np.mean(
            elev_n[np.array(Topography.tridata['triangles'])],
            axis=1
        )
        proj = Project(
            title='Topography'
        )
        Surface(
            project=proj,
            mesh=Mesh2D(
                vertices=Topography.tridata['vertices'],
                triangles=Topography.tridata['triangles']
            ),
            data=[
                dict(
                    location='N',
                    data=DataArray(
                        array=elev_n,
                        title='Elevation, vertices'
                    )
                ),
                dict(
                    location='CC',
                    data=DataArray(
                        array=elev_cc,
                        title='Elevation, faces'
                    )
                )
            ],
            textures=[
                Texture2DImage(
                    image=Topography.topo_image,
                    **Topography.topo_image_orientation
                )
            ],
            title='Topography Tri-Surface',
            description=('This surface has face and vertex elevation '
                         'data as well as surface imagery')
        )
        Surface(
            project=proj,
            mesh=Mesh2DGrid(
                h1=np.diff(Topography.griddata['x']),
                h2=np.diff(Topography.griddata['y']),
                Z=Topography.griddata['z'],
                O=[Topography.griddata['x'][0], Topography.griddata['y'][0], 0]
            ),
            data=[
                dict(
                    location='N',
                    data=DataArray(
                        array=Topography.griddata['z'],
                        title='Elevation, vertices'
                    )
                ),
            ],
            textures=[
                Texture2DImage(
                    image=Topography.topo_image,
                    **Topography.topo_image_orientation
                )
            ],
            title='Topography Grid-Surface',
            description=('This surface has vertex elevation '
                         'data as well as surface imagery')
        )
        return proj
