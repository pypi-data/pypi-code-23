"""volume.py contains the Volume composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
from numpy import ndarray
from six import string_types
import properties

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import MeshOptions
from .props import HasSteno3DProps


class _Mesh3DOptions(MeshOptions):
    pass


class _VolumeOptions(ColorOptions):
    pass


class Mesh3DGrid(BaseMesh):
    """Contains spatial information of a 3D grid volume."""

    h1 = properties.Array(
        doc='Tensor cell widths, x-direction',
        shape=('*',),
        dtype=(float, int)
    )
    h2 = properties.Array(
        doc='Tensor cell widths, y-direction',
        shape=('*',),
        dtype=(float, int)
    )
    h3 = properties.Array(
        doc='Tensor cell widths, z-direction',
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
    W = properties.Vector3(
        doc='Orientation of h3 axis',
        default='Z'
    )
    opts = properties.Instance(
        doc='Mesh3D Options',
        instance_class=_Mesh3DOptions,
        default=_Mesh3DOptions,
    )

    @property
    def nN(self):
        """ get number of nodes """
        return (len(self.h1)+1) * (len(self.h2)+1) * (len(self.h3)+1)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.h1) * len(self.h2) * len(self.h3)

    def _nbytes(self, arr=None):
        filenames = ('h1', 'h2', 'h3', 'O', 'U', 'V', 'W')
        if arr is None:
            return sum(self._nbytes(fn) for fn in filenames)
        if isinstance(arr, string_types) and arr in filenames:
            if getattr(self, arr, None) is None:
                return 0
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh3DGrid cannot calculate the number of '
                         'bytes of {}'.format(arr))

    def _get_dirty_data(self, force=False):
        datadict = super(Mesh3DGrid, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if force or ('h1' in dirty or 'h2' in dirty or 'h3' in dirty):
            datadict['tensors'] = dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
                h3=self.h3.tolist()
            ))
        if force or any([item in dirty for item in
                         ['O', 'U', 'V', 'W', 'h1', 'h2', 'h3']]):
            datadict['OUVZ'] = dumps(dict(
                O=self.O.tolist(),
                U=self.U.as_length(self.h1.sum()).tolist(),
                V=self.V.as_length(self.h2.sum()).tolist(),
                Z=self.W.as_length(self.h3.sum()).tolist()
            ))
        return datadict

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh3DGrid(
            title=kwargs['title'],
            description=kwargs['description'],
            h1=json['tensors']['h1'],
            h2=json['tensors']['h2'],
            h3=json['tensors']['h3'],
            O=json['OUVZ']['O'],
            U=json['OUVZ']['U'],
            V=json['OUVZ']['V'],
            W=json['OUVZ']['Z'],
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh3DGrid(
            h1=omf_geom.tensor_u,
            h2=omf_geom.tensor_v,
            h3=omf_geom.tensor_w,
            O=omf_geom.origin + omf_project.origin,
            U=omf_geom.axis_u,
            V=omf_geom.axis_v,
            W=omf_geom.axis_w
        )
        return mesh


class _VolumeBinder(HasSteno3DProps):
    """Contains the data on a 3D volume with location information"""
    location = properties.StringChoice(
        doc='Location of the data on mesh',
        choices={
            'CC': ('CELLCENTER'),
            # 'N': ('NODE', 'VERTEX', 'CORNER')
        },
        default='CC'
    )
    data = properties.Instance(
        doc='Data',
        instance_class=DataArray,
        default=DataArray,
    )


class Volume(CompositeResource):
    """Contains all the information about a 3D volume"""
    mesh = properties.Instance(
        doc='Mesh',
        instance_class=Mesh3DGrid,
        default=Mesh3DGrid,
    )
    data = properties.List(
        doc='Data',
        prop=_VolumeBinder,
        coerce=True,
        required=False,
        default=list,
    )
    opts = properties.Instance(
        doc='Options',
        instance_class=_VolumeOptions,
        default=_VolumeOptions,
    )

    def _nbytes(self):
        return self.mesh._nbytes() + sum(d.data._nbytes() for d in self.data)

    @properties.validator
    def _validate_data(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location == 'CC'  # in ('N', 'CC')
            valid_length = (
                self.mesh.nC if dat.location == 'CC'
                else self.mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'volume.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return True


__all__ = ['Volume', 'Mesh3DGrid']
