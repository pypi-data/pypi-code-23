"""line.py contains the Line composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from numpy import max as npmax
from numpy import min as npmin
from numpy import ndarray
from six import string_types
import properties

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import Options
from .props import array_serializer, array_download, HasSteno3DProps


class _Mesh1DOptions(Options):
    view_type = properties.StringChoice(
        doc='Display 1D lines or tubes/boreholes/extruded lines',
        choices={
            'line': ('lines', 'thin', '1d'),
            'tube': ('tubes', 'extruded line', 'extruded lines',
                     'borehole', 'boreholes')
        },
        default='line',
        required=False
    )


class _LineOptions(ColorOptions):
    pass


class Mesh1D(BaseMesh):
    """Contains spatial information of a 1D line set"""
    vertices = properties.Array(
        doc='Mesh vertices',
        shape=('*', 3),
        dtype=float,
        serializer=array_serializer,
        deserializer=array_download(('*', 3), (float,)),
    )
    segments = properties.Array(
        doc='Segment endpoint indices',
        shape=('*', 2),
        dtype=int,
        serializer=array_serializer,
        deserializer=array_download(('*', 2), (int,)),
    )
    opts = properties.Instance(
        doc='Options',
        instance_class=_Mesh1DOptions,
        default=_Mesh1DOptions,
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.segments)

    def _nbytes(self, arr=None):
        if arr is None:
            return self._nbytes('segments') + self._nbytes('vertices')
        if isinstance(arr, string_types) and arr in ('segments', 'vertices'):
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh1D cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @properties.observer(('segments', 'vertices'))
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_seg(self):
        if npmin(self.segments) < 0:
            raise ValueError('Segments may only have positive integers')
        if npmax(self.segments) >= len(self.vertices):
            raise ValueError('Segments expects more vertices than provided')
        self._validate_file_size('segments', self.segments)
        self._validate_file_size('vertices', self.vertices)
        return True

    def _get_dirty_files(self, force=False):
        files = super(Mesh1D, self)._get_dirty_files(force)
        dirty = self._dirty_props
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self._props['vertices'].serialize(self.vertices)
        if 'segments' in dirty or force:
            files['segments'] = \
                self._props['segments'].serialize(self.segments)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh1D(
            title=kwargs['title'],
            description=kwargs['description'],
            vertices=cls._props['vertices'].deserialize(
                json['vertices'],
            ),
            segments=cls._props['segments'].deserialize(
                json['segments'],
            ),
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh1D(
            vertices=(omf_geom.vertices.array +
                      omf_geom.origin +
                      omf_project.origin),
            segments=omf_geom.segments.array
        )
        return mesh


class _LineBinder(HasSteno3DProps):
    """Contains the data on a 1D line set with location information"""
    location = properties.StringChoice(
        doc='Location of the data on mesh',
        choices={
            'CC': ('LINE', 'FACE', 'CELLCENTER', 'EDGE', 'SEGMENT'),
            'N': ('VERTEX', 'NODE', 'ENDPOINT')
        }
    )
    data = properties.Instance(
        doc='Data',
        instance_class=DataArray,
        default=DataArray,
    )


class Line(CompositeResource):
    """Contains all the information about a 1D line set"""
    mesh = properties.Instance(
        doc='Mesh',
        instance_class=Mesh1D,
        default=Mesh1D,
    )
    data = properties.List(
        doc='Data',
        prop=_LineBinder,
        coerce=True,
        required=False,
        default=list,
    )
    opts = properties.Instance(
        doc='Options',
        instance_class=_LineOptions,
        default=_LineOptions,
    )

    def _nbytes(self):
        return self.mesh._nbytes() + sum(d.data._nbytes() for d in self.data)

    @properties.validator
    def _validate_data(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location in ('N', 'CC')
            valid_length = (
                self.mesh.nC if dat.location == 'CC'
                else self.mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'line.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return True


__all__ = ['Line', 'Mesh1D']
