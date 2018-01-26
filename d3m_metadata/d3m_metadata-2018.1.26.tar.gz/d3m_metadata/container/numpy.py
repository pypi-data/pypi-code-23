import datetime
import typing

import numpy  # type: ignore

from .. import metadata as metadata_module

__all__ = ('ndarray', 'matrix')

# This implementation is based on these guidelines:
# https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html

N = typing.TypeVar('N', bound='ndarray')
M = typing.TypeVar('M', bound='matrix')


# TODO: We could implement also __array_ufunc__ and adapt metadata as well after in-place changes to data?
class ndarray(numpy.ndarray):
    """
    Extended `numpy.ndarray` with the ``metadata`` attribute.

    Parameters
    ----------
    input_array : Sequence
        Anything array-like to create an instance from. Including lists and standard numpy arrays.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the array.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the array.
    """

    def __new__(cls: typing.Type[N], input_array: typing.Sequence, metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> N:
        array = numpy.asarray(input_array).view(cls)

        if metadata is not None:
            # TODO: We could merge "metadata with metadata from "input_array" if the latter is an instance of our ndarray.
            array.metadata = array.metadata.update((), metadata, source=source, timestamp=timestamp)

        return array

    def __array_finalize__(self, obj: typing.Any) -> None:
        # If metadata attribute already exists.
        if hasattr(self, 'metadata'):
            return

        if obj is not None and isinstance(obj, ndarray):
            # TODO: We could adapt (if this is after a slice) or copy existing metadata?
            self.metadata: metadata_module.DataMetadata = obj.metadata.clear(for_value=self)
        else:
            self.metadata = metadata_module.DataMetadata(for_value=self)


class matrix(numpy.matrix, ndarray):
    """
    Extended `numpy.matrix` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Union[Sequence, str]
        Anything array-like to create an instance from. Including lists and standard numpy arrays and matrices.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the matrix.
    dtype : Union[dtype, str]
         Data type of the output matrix.
    copy : bool
       If ``data`` is already an ``ndarray``, then this flag determines
       whether the data is copied (the default), or whether a view is
       constructed.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the matrix.
    """

    def __new__(cls: typing.Type[M], data: typing.Union[typing.Sequence, str], metadata: typing.Dict[str, typing.Any] = None,
                dtype: typing.Union[numpy.dtype, str] = None, copy: bool = True, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> M:
        mx = numpy.matrix.__new__(cls, data=data, dtype=dtype, copy=copy)

        if not isinstance(mx, cls):
            mx = mx.view(cls)

        if metadata is not None:
            # TODO: We could merge "metadata with metadata from "data" if the latter is an instance of our ndarray.
            mx.metadata = mx.metadata.update((), metadata, source=source, timestamp=timestamp)

        return mx

    def __array_finalize__(self, obj: typing.Any) -> None:
        numpy.matrix.__array_finalize__(self, obj)
        ndarray.__array_finalize__(self, obj)


typing.Sequence.register(numpy.ndarray)  # type: ignore
