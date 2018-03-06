"""tsyganenko.py provides an example Steno3D project of mag field lines"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .base import BaseExample, exampleproperty
from ..data import DataArray
from ..line import Mesh1D, Line
from ..project import Project


class Tsyganenko(BaseExample):
    """Class containing components of magnetic field lines project.

    Construct the project with Tsyganenko.get_project()
    """

    @exampleproperty
    def filenames(self):
        """all Tsyganenko files"""
        return ['tsyganenko_mag_field.txt', 'license.txt']

    @exampleproperty
    def datafile(self):
        """Tsyganenko data file"""
        return Tsyganenko.fetch_data(filename='tsyganenko_mag_field.txt',
                                     download_if_missing=False,
                                     verbose=False)

    @staticmethod
    def read_file(fname):
        verts = []
        segs = []
        data = []
        with open(fname, 'r') as f:
            for line in f:
                items = line.split()
                verts.append([float(i) for i in items[1:4]])
                data.append(float(items[4]))
                if items[0] != '1':
                    segs.append([len(verts)-2, len(verts)-1])
        return verts, segs, data

    @classmethod
    def get_project(self):
        """return rocket engine surface project"""
        verts, segs, data = Tsyganenko.read_file(Tsyganenko.datafile)
        proj = Project(
            title='Tsyganenko Magnetic Field',
            description='Simple model of the magnetic field of the Earth'
        )
        Line(
            project=proj,
            mesh=Mesh1D(
                vertices=verts,
                segments=segs,
            ),
            data=[
                dict(
                    location='N',
                    data=DataArray(
                        title='Magnitude of magnetic field (nT)',
                        array=data
                    )
                ),
                dict(
                    location='N',
                    data=DataArray(
                        title='Natural log of field (log(nT))',
                        array=np.log(data)
                    )
                )
            ],
            title='Magnetic Field Lines'
        )
        return proj
