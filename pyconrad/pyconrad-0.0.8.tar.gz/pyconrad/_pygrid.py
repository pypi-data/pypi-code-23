"""
Copyright (C) 2010-2017 - Andreas Maier
CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

"""

__author__ = "Stephan Seitz <stephan.seitz@fau.de>"
__copyright__ = "Andreas Maier <andreas.maier@fau.de> et al."
__license__ = """
pyCONRAD, python framework for cone beam radiology
Copyright (C) 2017 Stephan Seitz <stephan.seitz@fau.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import jpype
import numpy as np
from pyconrad._deprecated import deprecated

from .constants import java_float_dtype
from ._imageutils import ImageUtil
from jpype import JPackage


def grid_to_ndarray(grid):
    return PyGrid.from_grid(grid).view(np.ndarray)


def ndarray_to_grid(ndarray):
    return PyGrid.from_numpy(ndarray).grid

# Access Java array in C++ using JNI: http://www.math.uni-hamburg.de/doc/java/tutorial/native1.1/implementing/array.html


class PyGrid(np.ndarray):
    """


    """
    def __new__(cls, shape):
        return super().__new__(cls, shape=shape, dtype=java_float_dtype)

    def __init__(self, shape):
        self.__numericpackage = JPackage(
            'edu').stanford.rsl.conrad.data.numeric
        if not 0 < len(shape) < 5:
            raise Exception("shape dimension of %d not supported" % len(shape))
        self.__grid = getattr(self.__numericpackage,
                              "Grid{}D".format(len(shape)))(*reversed(shape))
        if shape[0] != 0:
            self.__dbuffer = jpype.nio.convertToDirectBuffer(self)

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(InfoArray, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. InfoArray():
        #    obj is None
        #    (we're in the middle of the InfoArray.__new__
        #    constructor, and self.info will be set when we return to
        #    InfoArray.__new__)
        if obj is None:
            return
        # From view casting - e.g arr.view(InfoArray):
        #    obj is arr
        #    (type(obj) can be InfoArray)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is InfoArray
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'info', because this
        # method sees all creation of default objects - with the
        # InfoArray.__new__ constructor, but also with
        # arr.view(InfoArray).
        # see InfoArray.__array_finalize__ for comments
        # self.info = getattr(obj, 'info', None)

    @classmethod
    def from_numpy(cls, array: np.ndarray):

        # if array.dtype != java_float_dtype:
        #     warnings.warn(
        #         "Warning: Numpy array is not of type pyconrad.java_float_dtype! Additional conversion necessary!")
        # must work on copy if not c-order contiguous (e.g. after swapped axes)

        # instance = np.ascontiguousarray(array, java_float_dtype).view(cls)
        instance = np.ascontiguousarray(array, java_float_dtype).view(cls)

        # instance.__dbuffer = jpype.nio.convertToDirectBuffer(array)
        instance.__numericpackage = JPackage(
            'edu').stanford.rsl.conrad.data.numeric

        if not 0 < array.ndim < 5:
            raise Exception("shape dimension of %d not supported" % array.ndim)
        instance.__grid = getattr(instance.__numericpackage, "Grid{}D".format(
            array.ndim))(*reversed(array.shape))

        # instance.update_grid()
        return instance

    @classmethod
    def from_grid(cls, grid):
        size = list(reversed(grid.getSize()[:]))
        numpy = np.zeros(size, java_float_dtype)
        instance = numpy.view(cls)
        instance.__grid = grid
        instance.__dbuffer = jpype.nio.convertToDirectBuffer(instance)
        instance.update_numpy()
        return instance

    @property
    def grid(self):
        if not hasattr(self, '__grid'):
            self.update_grid()
        return self.__grid

    def show(self, title=""):
        if not hasattr(self, '__grid'):
            self.update_grid()
        return self.__grid.show(title)

    def update_numpy(self):
        if not hasattr(self, '__dbuffer'):
            if not 0 < len(self.shape) < 5:
                raise Exception(
                    "shape dimension of %d not supported" % len(self.shape))

            if not self.flags['C_CONTIGUOUS'] or not self.flags['WRITEABLE']or not self.dtype == java_float_dtype:
                # self.data = np.ascontiguousarray(self).data
                copy = np.ascontiguousarray(self)
                if not self.flags['WRITEABLE']:
                    copy = copy.copy()
                self.data = copy.data

            assert self.flags['WRITEABLE']
            assert self.flags['C_CONTIGUOUS']  # writable & behaved

            self.__numericpackage = JPackage(
                'edu').stanford.rsl.conrad.data.numeric
            self.__dbuffer = jpype.nio.convertToDirectBuffer(self)

        shape = self.shape
        if 0 == shape[0]:
            return

        f_buffer = self.__dbuffer.asFloatBuffer()

        if len(shape) == 1:
            # Grid1D.getBuffer() would generate as copy of the original buffer
            # for i in range(shape[0]):
            #     self[i] = self.__gr
            self.__grid.notifyBeforeRead()
            f_buffer.put(self.__grid.buffer)

        elif len(shape) == 2:
            f_buffer.put(self.__grid.getBuffer())
        elif len(shape) is 3:
            f_buffer = self.__dbuffer.asFloatBuffer()
            for z in range(0, shape[0]):
                f_buffer.put(self.__grid.getSubGrid(
                    z).getBuffer())  # TODO: stride == 0?
        elif len(shape) is 4:
            f_buffer = self.__dbuffer.asFloatBuffer()
            for f in range(shape[0]):
                for z in range(shape[1]):
                    f_buffer.put(self.__grid.getSubGrid(f).getSubGrid(
                        z).getBuffer())  # TODO: stride == 0?
        else:
            raise Exception("shape dimension not supported")
        del self.__dbuffer

    def update_grid(self):
        if not hasattr(self, '__dbuffer'):
            if not 0 < len(self.shape) < 5:
                raise Exception(
                    "shape dimension of %d not supported" % len(self.shape))

            if not self.flags['C_CONTIGUOUS'] or not self.flags['WRITEABLE'] or not self.dtype == java_float_dtype:
                # self.data = np.ascontiguousarray(self).data
                copy = np.ascontiguousarray(self)
                if not self.flags['WRITEABLE']:
                    copy = copy.copy()
                self.data = copy.data

            assert self.flags['WRITEABLE']
            assert self.flags['C_CONTIGUOUS']  # writable & behaved

            self.__numericpackage = JPackage(
                'edu').stanford.rsl.conrad.data.numeric
            self.__dbuffer = jpype.nio.convertToDirectBuffer(self)
            self.__grid = getattr(self.__numericpackage, "Grid{}D".format(
                len(self.shape)))(*reversed(self.shape))

        shape = self.shape
        if 0 == shape[0]:
            return
        f_buffer = self.__dbuffer.asFloatBuffer()
        if len(shape) == 1:
            # Grid1D.getBuffer() would generate as copy of the original buffer
            self.__grid = self.__numericpackage.Grid1D(
                jpype.JArray(jpype.JFloat)(list(self[:])))
        elif len(shape) == 2:
            f_buffer.get(self.__grid.getBuffer())
        elif len(shape) is 3:
            for z in range(shape[0]):
                f_buffer.get(self.__grid.getSubGrid(
                    z).getBuffer())  # TODO: stride == 0?
        elif len(shape) is 4:
            for f in range(shape[0]):
                for z in range(shape[1]):
                    f_buffer.get(self.__grid.getSubGrid(f).getSubGrid(
                        z).getBuffer())  # TODO: stride == 0?
        else:
            raise Exception("shape dimension not supported")

        # del self.__dbuffer

    def save_tiff(self, path):
        ImageUtil.save_grid_as_tiff(self.__grid, path)

    @classmethod
    def from_tiff(cls, path):
        grid = ImageUtil.grid_from_tiff(path)
        return cls.from_grid(grid)

    @classmethod
    def from_image(cls, path):
        grid = ImageUtil.grid_from_tiff(path)
        return cls.from_grid(grid)

    def set_origin(self, vec):
        self.__grid.setOrigin(jpype.JArray(jpype.JDouble)(vec))

    def set_spacing(self, vec):
        self.__grid.setSpacing(jpype.JArray(jpype.JDouble)(vec))

    @staticmethod
    def java_float_dtype():
        return java_float_dtype

    def __str__(self):
        return super(PyGrid, self).__str__()

    def __getitem__(self, item):
        return super(PyGrid, self).__getitem__(item)

    def save_vtk(self, file, title="pygrid"):
        from pyevtk.hl import imageToVTK
        if np.abs(self.grid.getSpacing()[0]) < 1e-5:
            spacing = [1.] * len(self.shape)
        else:
            spacing = tuple(self.grid.getSpacing()[:])
        imageToVTK(file, tuple(self.grid.getOrigin()[
                   :]), spacing, cellData={title: np.array(self)})
