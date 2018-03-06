from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple, OrderedDict
from io import BytesIO
from tempfile import NamedTemporaryFile

import numpy as np
from requests import get
import properties


class HasSteno3DProps(properties.HasProperties):

    _REGISTRY = OrderedDict()

    def __init__(self, **metadata):
        self._dirty_props = set()
        super(HasSteno3DProps, self).__init__(**metadata)

    def _get(self, name):
        value = super(HasSteno3DProps, self)._get(name)
        # Returning a copy of the list maintains backward compatibility
        # until properties has better handling of lists.
        if isinstance(value, list):
            value = [val for val in value]
        return value

    @properties.observer(properties.everything)
    def _mark_dirty(self, change):
        self._dirty_props.add(change['name'])

    def _mark_clean(self, recurse=True):
        self._dirty_props = set()
        if not recurse or getattr(self, '_inside_clean', False):
            return
        self._inside_clean = True
        try:
            props = self._dirty
            for prop in props:
                value = getattr(self, prop)
                if isinstance(value, properties.HasProperties):
                    value._mark_clean()
                if isinstance(value, (list, tuple)):
                    for v in value:
                        if isinstance(v, properties.HasProperties):
                            v._mark_clean()
        finally:
            self._inside_clean = False

    @property
    def _dirty(self):
        if getattr(self, '_inside_dirty', False):
            return set()
        dirty_instances = set()
        self._inside_dirty = True
        try:
            props = self._non_deprecated_props()
            for prop in props:
                value = getattr(self, prop)
                if (isinstance(value, properties.HasProperties) and
                        len(value._dirty) > 0):
                    dirty_instances.add(prop)
                if isinstance(value, (list, tuple)):
                    for v in value:
                        if (isinstance(v, properties.HasProperties) and
                                len(v._dirty) > 0):
                            dirty_instances.add(prop)
        finally:
            self._inside_dirty = False
        return self._dirty_props.union(dirty_instances)

    def _non_deprecated_props(self):
        return {k: v for k, v in self._props.items()
                if not isinstance(v, properties.Renamed)}


def image_download(url, **kwargs):
    im_resp = get(url, timeout=60)
    if im_resp.status_code != 200:
        raise IOError('Failed to download image.')
    output = BytesIO()
    output.name = 'texture.png'
    for chunk in im_resp:
        output.write(chunk)
    output.seek(0)
    return output


FileProp = namedtuple('FileProp', ['file', 'dtype'])


def array_serializer(data, **kwargs):
    """Convert the array data to a serialized binary format"""
    if isinstance(data.flatten()[0], np.floating):
        use_dtype = '<f4'
        nan_mask = ~np.isnan(data)
        assert np.allclose(
                data.astype(use_dtype)[nan_mask], data[nan_mask]), \
            'Converting the type should not screw things up.'
    elif isinstance(data.flatten()[0], np.integer):
        use_dtype = '<i4'
        assert (data.astype(use_dtype) == data).all(), \
            'Converting the type should not screw things up.'
    else:
        raise TypeError('Must be a float or an int: {}'.format(data.dtype))

    data_file = NamedTemporaryFile('rb+', suffix='.dat')
    data.astype(use_dtype).tofile(data_file.file)
    data_file.seek(0)
    return FileProp(data_file, use_dtype)


class array_download(object):

    def __init__(self, shape, dtype):
        self.shape = shape
        self.dtype = dtype

    def __call__(self, url, **kwargs):
        arr_resp = get(url, timeout=60)
        if arr_resp.status_code != 200:
            raise IOError('Failed to download array.')
        data_file = NamedTemporaryFile()
        for chunk in arr_resp:
            data_file.write(chunk)
        data_file.seek(0)
        if self.dtype[0] is int:
            dtype = '<i4'
        elif self.dtype[0] is float:
            dtype = '<f4'
        else:
            raise ValueError('Invalid dtype {}'.format(self.dtype))
        arr = np.fromfile(data_file.file, dtype)
        unknown_dim = len(arr)
        for dim in self.shape:
            if dim == '*':
                continue
            unknown_dim /= dim
        if '*' in self.shape:
            assert abs(unknown_dim - int(unknown_dim)) < 1e-9, 'bad shape'
            shape = tuple(
                (int(unknown_dim) if dim == '*' else dim for dim in self.shape)
            )
        else:
            assert abs(unknown_dim) < 1e-9, 'bad shape'
            shape = self.shape
        arr = arr.reshape(shape)
        data_file.close()
        return arr
