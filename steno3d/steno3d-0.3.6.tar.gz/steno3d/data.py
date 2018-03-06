"""data.py contains resource data structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
import random
from six import string_types

import numpy as np
import properties

from .base import BaseData
from .props import array_serializer, array_download


class DataArray(BaseData):
    """Data array with unique values at every point in the mesh

    .. note:

        DataArray custom colormap is currently unsupported on
        steno3d.com
    """
    _resource_class = 'array'
    array = properties.Array(
        doc='Data, unique values at every point in the mesh',
        shape=('*',),
        dtype=(float, int),
        serializer=array_serializer,
        deserializer=array_download(('*',), (float, int)),
    )

    order = properties.StringChoice(
        doc='Data array order, for data on grid meshes',
        choices={
            'c': ('C-STYLE', 'NUMPY', 'ROW-MAJOR', 'ROW'),
            'f': ('FORTRAN', 'MATLAB', 'COLUMN-MAJOR', 'COLUMN', 'COL')
        },
        default='c',
    )
    colormap = properties.List(
        doc='Colormap applied to data range or categories',
        prop=properties.Color(''),
        min_length=1,
        max_length=256,
        required=False,
    )

    def __init__(self, array=None, **kwargs):
        super(DataArray, self).__init__(**kwargs)
        if array is not None:
            self.array = array

    def _nbytes(self, arr=None):
        if arr is None or (isinstance(arr, string_types) and arr == 'array'):
            arr = self.array
        if isinstance(arr, np.ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('DataArray cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @properties.observer('array')
    def _reject_large_files(self, change):
        self._validate_file_size(change['name'], change['value'])

    @properties.validator
    def _validate_array(self):
        self._validate_file_size('array', self.array)
        return True

    def _get_dirty_data(self, force=False):
        datadict = super(DataArray, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if 'order' in dirty or force:
            datadict['order'] = self.order
        if self.colormap and ('colormap' in dirty or force):
            datadict['colormap'] = dumps(self.colormap)
        return datadict

    def _get_dirty_files(self, force=False):
        files = super(DataArray, self)._get_dirty_files(force)
        dirty = self._dirty_props
        if 'array' in dirty or force:
            files['array'] = self._props['array'].serialize(self.array)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        data = DataArray(
            title=kwargs['title'],
            description=kwargs['description'],
            order=json['order'],
            array=cls._props['array'].deserialize(
                json['array'],
            )
        )
        if json.get('colormap'):
            data.colormap = json['colormap']
        return data

    @classmethod
    def _build_from_omf(cls, omf_data):
        assert omf_data.__class__.__name__ in ('ScalarData', 'MappedData')
        data = dict(
            location='N' if omf_data.location == 'vertices' else 'CC',
            data=DataArray(
                title=omf_data.name,
                description=omf_data.description,
                array=omf_data.array.array
            )
        )
        return data


def index_serializer(data, **kwargs):
    """Serializes int indices as floats, where -1 is replaced with NaN"""
    data = data.astype(float)
    data = np.where(data == -1.0, np.nan, data)
    return array_serializer(data, **kwargs)


class index_download(array_download):
    """Download index array as floats and convert to ints

    This replaces NaN values with -1
    """

    def __init__(self, shape):
        self.shape = shape
        self.dtype = (float,)

    def __call__(self, url, **kwargs):
        arr = super(index_download, self).__call__(url, **kwargs)
        arr = np.where(np.isnan(arr), -1, arr)
        arr = arr.astype(int)
        return arr

def generate_colormap(map_len):
    """Generate a random colormap given length map_len"""
    if map_len <= len(properties.basic.COLORS_20):
        return random.sample(properties.basic.COLORS_20, map_len)
    if map_len <= len(properties.basic.COLORS_NAMED):
        return random.sample(list(properties.basic.COLORS_NAMED), map_len)
    if map_len > 256**3:
        raise ValueError('max colormap length must be less than 256**3')
    map_ints = random.sample(range(256**3), map_len)
    def color_from_int(value):
        r = int(value % 256)
        g = int((value-r)/256 % 256)
        b = int(((value-r)/256-g)/256 % 256)
        return (r, g, b)
    return [color_from_int(value) for value in map_ints]

class DataCategory(DataArray):
    """Data array with indices and corresponding string categories

    For locations with no data, use -1 for index.
    If colormap is unspecified, colors will be randomized.
    """
    _resource_class = 'category'
    array = properties.Array(
        doc='Category index values at every point in the mesh',
        shape=('*',),
        dtype=(int,),
        serializer=index_serializer,
        deserializer=index_download(('*',)),
    )
    categories = properties.List(
        doc='List of string categories',
        prop=properties.String(''),
        min_length=1,
        max_length=256,
        required=False,
    )

    @properties.validator
    def _categories_and_colormap(self):
        if (
                (self.categories and self.colormap) and
                len(self.categories) != len(self.colormap)
        ):
            raise ValueError('categories and colormap must be equal length')

    @properties.validator
    def _categories_and_array(self):
        if min(self.array) < -1:
            raise ValueError('array indices must be >= -1')
        if max(self.array) >= 256:
            raise ValueError('array indices must be < 256')
        if self.categories and max(self.array) >= len(self.categories):
            raise ValueError('array indices must be < len(categories)')
        if self.colormap and max(self.array) >= len(self.colormap):
            raise ValueError('array indices must be < len(colormap)')

    @properties.validator
    def _populate_colormap(self):
        if self.colormap:
            return
        self._categories_and_array()
        self.colormap = self._random_colormap()

    @properties.validator
    def _populate_categories(self):
        if self.categories:
            return
        self._categories_and_array()
        if self.categories:
            cat_len = len(self.categories)
        else:
            cat_len = max(self.array) + 1
        self.categories = ['']*cat_len

    @properties.validator('array')
    def _array_gt_zero(self, change):
        if min(change['value']) < -1:
            raise ValueError('array indices must be >= -1')

    def _get_dirty_data(self, force=False):
        datadict = super(DataCategory, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if 'categories' in dirty or force:
            datadict['categories'] = dumps(self.categories)
        return datadict

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        data = DataCategory(
            title=kwargs['title'],
            description=kwargs['description'],
            order=json['order'],
            array=cls._props['array'].deserialize(
                json['array'],
            ),
            colormap=json['colormap'],
            categories=json['categories'],
        )
        return data

    def _random_colormap(self):
        if self.categories:
            map_len = len(self.categories)
        elif self.array is not None:
            map_len = max(self.array) + 1
        else:
            raise ValueError('categories or array indeces are required for '
                             'random colormap')
        return generate_colormap(map_len)



class DataDiscrete(DataArray):
    """Continuous data array with discreet color spans"""

    _resource_class = 'discrete'

    range_visibility = properties.List(
        'True (1) if color category is visible',
        prop=properties.Integer('', cast=True),
        required=False,
    )
    end_values = properties.List(
        'end values of discrete categories; '
        '-inf/inf are lower/upper bounds',
        prop=properties.Float('', cast=True),
    )
    end_inclusive = properties.List(
        'True (1) if end values are inclusive for lower range',
        prop=properties.Integer('', cast=True),
        required=False,
    )

    @properties.validator('end_values')
    def _end_values_increasing(self, change):
        vals = np.array(change['value'])
        if not np.all(np.isfinite(vals)):
            raise ValueError('All end values must be finite')
        diffs = vals[1:] - vals[:-1]
        if np.any(diffs < 0):
            raise ValueError('End values must not decrease')

    @properties.validator(['range_visibility', 'end_inclusive'])
    def _int_arrays_are_bools(self, change):
        if not all([v in (0, 1) for v in change['value']]):
            raise ValueError('range_visibility and end_inclusive must be '
                             '1s or 0s')

    @properties.validator
    def _generate_props_validate_lengths(self):
        if self.end_inclusive is None:
            self.end_inclusive = [True]*len(self.end_values)
        if self.range_visibility is None:
            self.range_visibility = [True]*(len(self.end_values)+1)
        if self.colormap is None:
            self.colormap = generate_colormap(len(self.end_values)+1)
        if len(self.colormap) != len(self.end_values) + 1:
            raise ValueError('If end_values is length N, colormap must '
                             'be length N + 1')
        if len(self.range_visibility) != len(self.end_values) + 1:
            raise ValueError('If end_values is length N, range_visibility must '
                             'be length N + 1')
        if len(self.end_inclusive) != len(self.end_values):
            raise ValueError('Length of end_inclusive must equal length end_values')

    def _get_dirty_data(self, force=False):
        datadict = super(DataDiscrete, self)._get_dirty_data(force)
        dirty = self._dirty_props
        if 'end_values' in dirty or force:
            datadict['end_values'] = dumps(self.end_values)
        if 'end_inclusive' in dirty or force:
            datadict['end_inclusive'] = dumps(self.end_inclusive)
        if 'range_visibility' in dirty or force:
            datadict['range_visibility'] = dumps(self.range_visibility)
        return datadict

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        data = DataDiscrete(
            title=kwargs['title'],
            description=kwargs['description'],
            order=json['order'],
            array=cls._props['array'].deserialize(
                json['array'],
            ),
            colormap=json['colormap'],
            end_values=json['end_values'],
            end_inclusive=json['end_inclusive'],
            range_visibility=json['range_visibility'],
        )
        return data

__all__ = ['DataArray', 'DataCategory', 'DataDiscrete']
