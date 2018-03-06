"""brain.py provides an example Steno3D project of brain volume"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import os
from six import text_type

from .base import BaseExample, exampleproperty
from ..data import DataArray
from ..project import Project
from ..volume import Mesh3DGrid, Volume


class Brain(BaseExample):
    """Class containing components of brain volume project.

    Construct the project with Brain.get_project()
    """

    @exampleproperty
    def filenames(self):
        """all brain files"""
        bin_files = ['MRbrain.' + text_type(i) for i in range(1, 110)]
        return bin_files + ['info.txt', 'announcement.txt', 'license.txt']

    @exampleproperty
    def datafiles(self):
        """brain data files"""
        filepaths = [
            Brain.fetch_data(filename=fn,
                             download_if_missing=False,
                             verbose=False)
            for fn in Brain.filenames[:-3]
        ]
        return filepaths

    @exampleproperty
    def datavolume(self):
        """return full numpy volume of brain data"""
        dataall = []
        for filename in Brain.datafiles:
            x = np.fromfile(filename, dtype='>i2')
            dataall.append(x.reshape((256, 256), order ='C'))
        return np.array(dataall).astype(float)

    @classmethod
    def get_project(self):
        """return brain volume project"""
        data = Brain.datavolume[::, -30:-210:-2, -30:-210:-2]
        proj = Project(
            title='Brain MRI',
            description='Project with brain volume'
        )
        Volume(
            project=proj,
            mesh=Mesh3DGrid(
                h1=np.ones(data.shape[0]),
                h2=np.ones(data.shape[1]),
                h3=np.ones(data.shape[2]),
            ),
            data=dict(
                location='CC',
                data=DataArray(
                    title='MRI brain data',
                    array=data.flatten()
                )
            ),
            title='Brain Volume'
        )
        return proj
