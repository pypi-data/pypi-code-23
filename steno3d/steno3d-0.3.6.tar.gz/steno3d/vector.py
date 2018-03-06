"""vector.py contains the Vector composite resource for Steno3D"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import properties

from .base import CompositeResource
from .options import ColorOptions

from .point import Mesh0D, _PointBinder
from .props import array_serializer, array_download


class _VectorOptions(ColorOptions):
    pass


class Vector(CompositeResource):
    """Contains all the information about a vector field"""

    _resource_class = 'vector'

    mesh = properties.Instance(
        doc='Mesh',
        instance_class=Mesh0D,
        default=Mesh0D,
    )
    vectors = properties.Array(
        doc='Vector',
        shape=('*', 3),
        dtype=float,
        serializer=array_serializer,
        deserializer=array_download(('*', 3), (float,)),
    )
    data = properties.List(
        doc='Data',
        prop=_PointBinder,
        coerce=True,
        required=False,
        default=list,
    )
    opts = properties.Instance(
        doc='Options',
        instance_class=_VectorOptions,
        default=_VectorOptions,
    )

    def _nbytes(self):
        return (self.mesh._nbytes() + self.vectors.astype('f4').nbytes +
                sum(d.data._nbytes() for d in self.data))

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

    @properties.validator
    def _validate_vectors(self):
        """Check if vectors is built correctly"""
        valid_length = self.mesh.nN
        if len(self.vectors) != valid_length:
            raise ValueError(
                'vectors length {datalen} does not match '
                'mesh vertex length {meshlen}'.format(
                    datalen=len(proposal['value']),
                    meshlen=valid_length
                )
            )
        return True

    def _get_dirty_files(self, force=False):
        files = {}
        dirty = self._dirty_props
        if 'vectors' in dirty or force:
            files['vectors'] = \
                self._props['vectors'].serialize(self.vectors)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        vec = super(Vector, cls)._build_from_json(json, **kwargs)
        vec.vectors = cls._props['vectors'].deserialize(
            json['vectors'],
        )
        return vec


__all__ = ['Vector']
