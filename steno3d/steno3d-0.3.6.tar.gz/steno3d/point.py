"""point.py contains the Point composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import string_types

from numpy import ndarray
import properties

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import Options
from .texture import Texture2DImage
from .props import array_serializer, array_download, HasSteno3DProps


class _Mesh0DOptions(Options):
    pass


class _PointOptions(ColorOptions):
    pass


class Mesh0D(BaseMesh):
    """Contains spatial information of a 0D point cloud."""
    vertices = properties.Array(
        doc='Point locations',
        shape=('*', 3),
        dtype=float,
        serializer=array_serializer,
        deserializer=array_download(('*', 3), (float,)),
    )
    opts = properties.Instance(
        doc='Mesh0D Options',
        instance_class=_Mesh0DOptions,
        default=_Mesh0DOptions,
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    def _nbytes(self, arr=None):
        if arr is None or (isinstance(arr, string_types) and
                           arr == 'vertices'):
            arr = self.vertices
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh0D cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @properties.validator('vertices')
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_verts(self):
        """Check if mesh content is built correctly"""
        self._validate_file_size('vertices', self.vertices)
        return True

    def _get_dirty_files(self, force=False):
        files = super(Mesh0D, self)._get_dirty_files(force)
        dirty = self._dirty_props
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self._props['vertices'].serialize(self.vertices)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh0D(
            title=kwargs['title'],
            description=kwargs['description'],
            vertices=cls._props['vertices'].deserialize(
                json['vertices'],
            ),
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh0D(
            vertices=(omf_geom.vertices.array +
                      omf_geom.origin +
                      omf_project.origin)
        )
        return mesh


class _PointBinder(HasSteno3DProps):
    """Contains the data on a 0D point cloud"""
    location = properties.StringChoice(
        doc='Location of the data on mesh',
        default='N',
        choices={
            'N': ('NODE', 'CELLCENTER', 'CC', 'VERTEX')
        }
    )
    data = properties.Instance(
        doc='Data',
        instance_class=DataArray,
        default=DataArray,
    )


class Point(CompositeResource):
    """Contains all the information about a 0D point cloud"""
    mesh = properties.Instance(
        doc='Mesh',
        instance_class=Mesh0D,
        default=Mesh0D,
    )
    data = properties.List(
        doc='Data',
        prop=_PointBinder,
        coerce=True,
        required=False,
        default=list,
    )
    textures = properties.List(
        doc='Textures',
        prop=Texture2DImage,
        coerce=True,
        required=False,
        default=list,
    )
    opts = properties.Instance(
        doc='Options',
        instance_class=_PointOptions,
        default=_PointOptions,
    )

    def _nbytes(self):
        return (self.mesh._nbytes() +
                sum(d.data._nbytes() for d in self.data) +
                sum(t._nbytes() for t in self.textures))

    @properties.validator
    def _validate_data(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location == 'N'
            valid_length = self.mesh.nN
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'point.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return True


__all__ = ['Point', 'Mesh0D']
