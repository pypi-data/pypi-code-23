from __future__ import absolute_import

from .ffi import FFI

try:
    try:
        import numpypy
    except ImportError:
        pass
    import numpy
except ImportError:
    numpy = None


class nparray(object):
    """
    For use with cffi arrays, return a numpy reference to them that also holds
    a reference to the c data to ensure it stays alive
    :param cffi.CData _cdata: array object, expected to be uint8_t or equivalent
    :return: wrapped numpy array object
    """
    def __init__(self, _cdata, size=-1, dtype=None, ffi=None):
        if not numpy:
            raise NotImplementedError("numpy needs to be installed to use nparray()")
        if ffi is None:
            ffi = FFI()
        if not ffi:
            raise ValueError("Need to provide ffi argument when cffi not installed")

        dtype = dtype or numpy.uint8
        self.__cdata = _cdata
        self.__buff = ffi.buffer(_cdata, size=size)
        self.__nparray = numpy.frombuffer(self.__buff, dtype=dtype)

    def __getattr__(self, item):
        return getattr(self.__nparray, item)

    def __getitem__(self, item):
        return self.__nparray[item]

    def __repr__(self):
        return repr(self.__nparray)

    def __len__(self):
        return len(self.__nparray)

    def __eq__(self, other):
        if not isinstance(other, nparray):
            other = nparray(other)
        return numpy.array_equal(self, other)

    @property
    def ndarray(self):
        return self.__nparray


def nparrayptr(nparr, offset=0):
    """ Convenience function for getting the CFFI-compatible pointer to a numpy
    array object. """
    return FFI().cast('void *', nparr.__array_interface__['data'][0]+offset)


def carray(items_or_size=None, size=None, ctype='int'):
    """ Convenience function for creating C arrays. """

    if isinstance(items_or_size, int) and size is None:
        size = items_or_size
        items = None
    else:
        items = items_or_size

    ffi = FFI()
    if items and size and size > len(items):
        size = max(len(items), size or 0)
        arr = ffi.new(ffi.getctype(ctype, '[]'), size)
        for i, elem in enumerate(items):
            arr[i] = elem
        return arr
    else:
        return ffi.new(ffi.getctype(ctype, '[]'), items or size)