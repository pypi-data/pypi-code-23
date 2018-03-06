"""surface.py contains the Surface composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps

from numpy import max as npmax
from numpy import min as npmin
from numpy import ndarray
from six import string_types
import properties

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import MeshOptions
from .texture import Texture2DImage
from .props import array_serializer, array_download, HasSteno3DProps


class _Mesh2DOptions(MeshOptions):
    pass


class _SurfaceOptions(ColorOptions):
    pass


class Mesh2D(BaseMesh):
    """class steno3d.Mesh2D

    Contains spatial information about a 2D surface defined by
    triangular faces.
    """
    vertices = properties.Array(
        doc='Mesh vertices',
        shape=('*', 3),
        dtype=float,
        serializer=array_serializer,
        deserializer=array_download(('*', 3), (float,)),
    )
    triangles = properties.Array(
        doc='Mesh triangle vertex indices',
        shape=('*', 3),
        dtype=int,
        serializer=array_serializer,
        deserializer=array_download(('*', 3), (int,)),
    )
    opts = properties.Instance(
        doc='Mesh2D Options',
        instance_class=_Mesh2DOptions,
        default=_Mesh2DOptions,
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.triangles)

    def _nbytes(self, arr=None):
        if arr is None:
            return self._nbytes('vertices') + self._nbytes('triangles')
        if isinstance(arr, string_types) and arr in ('vertices', 'triangles'):
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh2D cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @properties.validator(('triangles', 'vertices'))
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_tri(self):
        if npmin(self.triangles) < 0:
            raise ValueError('Triangles may only have positive integers')
        if npmax(self.triangles) >= len(self.vertices):
            raise ValueError('Triangles expects more vertices than provided')
        self._validate_file_size('triangles', self.triangles)
        self._validate_file_size('vertices', self.vertices)
        return True

    def _get_dirty_files(self, force=False):
        files = {}
        dirty = self._dirty_props
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self._props['vertices'].serialize(self.vertices)
        if 'triangles' in dirty or force:
            files['triangles'] = \
                self._props['triangles'].serialize(self.triangles)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh2D(
            title=kwargs['title'],
            description=kwargs['description'],
            vertices=cls._props['vertices'].deserialize(
                json['vertices'],
            ),
            triangles=cls._props['triangles'].deserialize(
                json['triangles'],
            ),
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh2D(
            vertices=(omf_geom.vertices.array +
                      omf_geom.origin +
                      omf_project.origin),
            triangles=omf_geom.triangles.array
        )
        return mesh


class Mesh2DGrid(BaseMesh):
    """Contains spatial information of a 2D grid."""
    h1 = properties.Array(
        doc='Grid cell widths, U-direction',
        shape=('*',),
        dtype=(float, int)
    )
    h2 = properties.Array(
        doc='Grid cell widths, V-direction',
        shape=('*',),
        dtype=(float, int)
    )
    x0 = properties.Renamed('O')
    O = properties.Vector3(
        doc='Origin vector',
        default=[0., 0., 0.]
    )
    U = properties.Vector3(
        doc='Orientation of h1 axis',
        default='X'
    )
    V = properties.Vector3(
        doc='Orientation of h2 axis',
        default='Y'
    )
    Z = properties.Array(
        doc='Node topography',
        shape=('*',),
        dtype=float,
        default=[],
        required=False,
        serializer=array_serializer,
        deserializer=array_download(('*',), (float,)),
    )
    opts = properties.Instance(
        doc='Mesh2D Options',
        instance_class=_Mesh2DOptions,
        default=_Mesh2DOptions,
    )

    @property
    def nN(self):
        """ get number of nodes """
        return (len(self.h1)+1) * (len(self.h2)+1)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.h1) * len(self.h2)

    def _nbytes(self, arr=None):
        filenames = ('h1', 'h2', 'O', 'U', 'V', 'Z')
        if arr is None:
            return sum(self._nbytes(fn) for fn in filenames)
        if isinstance(arr, string_types) and arr in filenames:
            if getattr(self, arr, None) is None:
                return 0
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh2DGrid cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @properties.observer('Z')
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_Z(self):
        """Check if mesh content is built correctly"""
        if self.Z is None or len(self.Z) == 0:
            return True
        if len(self.Z) != self.nN:
            raise ValueError(
                'Length of Z, {zlen}, must equal number of nodes, '
                '{nnode}'.format(
                    zlen=len(self.Z),
                    nnode=self.nN
                )
            )
        self._validate_file_size('Z', self.Z)
        return True

    def _get_dirty_data(self, force=False):
        datadict = super(Mesh2DGrid, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if ('h1' in dirty or 'h2' in dirty) or force:
            datadict['tensors'] = dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
            ))
        if ('O' in dirty or 'U' in dirty or 'V' in dirty) or force:
            datadict['OUV'] = dumps(dict(
                O=self.O.tolist(),
                U=self.U.as_length(self.h1.sum()).tolist(),
                V=self.V.as_length(self.h2.sum()).tolist(),
            ))
        return datadict

    def _get_dirty_files(self, force=False):
        files = super(Mesh2DGrid, self)._get_dirty_files(force)
        dirty = self._dirty_props
        if 'Z' in dirty or (force and getattr(self, 'Z', []) != []):
            files['Z'] = self._props['Z'].serialize(self.Z)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh2DGrid(
            title=kwargs['title'],
            description=kwargs['description'],
            h1=json['tensors']['h1'],
            h2=json['tensors']['h2'],
            O=json['OUV']['O'],
            U=json['OUV']['U'],
            V=json['OUV']['V'],
            opts=json['meta']
        )
        try:
            mesh.Z = cls._props['Z'].deserialize(
                json['Z'],
            )
        except:
            mesh.Z = []

        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh2DGrid(
            h1=omf_geom.tensor_u,
            h2=omf_geom.tensor_v,
            O=omf_geom.origin + omf_project.origin,
            U=omf_geom.axis_u,
            V=omf_geom.axis_v
        )
        if omf_geom.offset_w is not None:
            mesh.Z = omf_geom.offset_w.array
        return mesh


class _SurfaceBinder(HasSteno3DProps):
    """Contains the data on a 2D surface with location information"""
    location = properties.StringChoice(
        doc='Location of the data on mesh',
        choices={
            'CC': ('FACE', 'CELLCENTER'),
            'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = properties.Instance(
        doc='Data',
        instance_class=DataArray,
        default=DataArray,
    )


class Surface(CompositeResource):
    """Contains all the information about a 2D surface"""
    mesh = properties.Union(
        doc='Mesh',
        props=(
            properties.Instance('', Mesh2D, default=Mesh2D),
            properties.Instance('', Mesh2DGrid)
        )
    )
    data = properties.List(
        doc='Data',
        prop=_SurfaceBinder,
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
        instance_class=_SurfaceOptions,
        default=_SurfaceOptions,
    )

    def _nbytes(self):
        return (self.mesh._nbytes() +
                sum(d.data._nbytes() for d in self.data) +
                sum(t._nbytes() for t in self.textures))

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
                    'surface.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return True


__all__ = ['Surface', 'Mesh2D', 'Mesh2DGrid']
