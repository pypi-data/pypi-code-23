import datetime
import typing

import numpy  # type: ignore
import pandas  # type: ignore
from pandas.core.dtypes import common as pandas_common  # type: ignore

from .. import metadata as metadata_module

__all__ = ('DataFrame', 'SparseDataFrame')

# This implementation is based on these guidelines:
# https://pandas.pydata.org/pandas-docs/stable/internals.html#subclassing-pandas-data-structures

D = typing.TypeVar('D', bound='DataFrame')


class DataFrame(pandas.DataFrame):
    """
    Extended `pandas.DataFrame` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Sequence
        Anything array-like to create an instance from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the data frame.
    index : Union[Index, Sequence]
        Index to use for resulting frame.
    columns : Union[Index, Sequence]
        Column labels to use for resulting frame.
    dtype : Union[dtype, str, ExtensionDtype]
        Data type to force.
    copy : bool
        Copy data from inputs.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the data frame.
    """

    @property
    def _constructor(self) -> type:
        return DataFrame

    def __init__(self, data: typing.Sequence = None, metadata: typing.Dict[str, typing.Any] = None, index: typing.Union[pandas.Index, typing.Sequence] = None,
                 columns: typing.Union[pandas.Index, typing.Sequence] = None, dtype: typing.Union[numpy.dtype, str, pandas_common.ExtensionDtype] = None, copy: bool = False,
                 *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        # If not a constructor call to this exact class, then a child constructor
        # is responsible to call a pandas contructor.
        if type(self) is DataFrame:
            pandas.DataFrame.__init__(self, data=data, index=index, columns=columns, dtype=dtype, copy=copy)

        if isinstance(data, DataFrame):
            # TODO: We could copy and merge with "metadata"?
            self.metadata: metadata_module.DataMetadata = data.metadata.clear(for_value=self, source=source, timestamp=timestamp)

            if metadata is not None:
                self.metadata = self.metadata.update((), metadata, source=source, timestamp=timestamp)
        else:
            self.metadata = metadata_module.DataMetadata(metadata, for_value=self, source=source, timestamp=timestamp)

    def __finalize__(self: D, other: typing.Any, method: str = None, **kwargs: typing.Any) -> D:
        self = super().__finalize__(other, method, **kwargs)

        # If metadata attribute already exists.
        if hasattr(self, 'metadata'):
            return self

        # Merge operation: using metadata of the left object.
        if method == 'merge':
            obj = other.left
        # Concat operation: using metadata of the first object.
        elif method == 'concat':
            obj = other.objs[0]
        else:
            obj = other

        if isinstance(obj, DataFrame):
            # TODO: We could adapt (if this is after a slice) or copy existing metadata?
            self.metadata: metadata_module.DataMetadata = obj.metadata.clear(for_value=self)
        else:
            self.metadata = metadata_module.DataMetadata(for_value=self)

        return self


class SparseDataFrame(pandas.SparseDataFrame, DataFrame):
    """
    Extended `pandas.SparseDataFrame` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Sequence
        Anything array-like to create an instance from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the sparse data frame.
    index : Union[Index, Sequence]
        Index to use for resulting frame.
    columns : Union[Index, Sequence]
        Column labels to use for resulting frame.
    default_kind : str
        Default sparse kind for converting `Series` to `SparseSeries`.
    default_fill_value : float
        Default fill_value for converting `Series` to `SparseSeries`.
    dtype : Union[dtype, str, ExtensionDtype]
        Data type to force.
    copy : bool
        Copy data from inputs.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the sparse data frame.
    """

    @property
    def _constructor(self) -> type:
        return SparseDataFrame

    def __init__(self, data: typing.Sequence = None, metadata: typing.Dict[str, typing.Any] = None, index: typing.Union[pandas.Index, typing.Sequence] = None,
                 columns: typing.Union[pandas.Index, typing.Sequence] = None, default_kind: str = None, default_fill_value: float = None,
                 dtype: typing.Union[numpy.dtype, str, pandas_common.ExtensionDtype] = None, copy: bool = False,
                 *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        pandas.SparseDataFrame.__init__(self, data=data, index=index, columns=columns, default_kind=default_kind, default_fill_value=default_fill_value, dtype=dtype, copy=copy)
        DataFrame.__init__(self, data=data, metadata=metadata, index=index, columns=columns, source=source, timestamp=timestamp)


typing.Sequence.register(pandas.DataFrame)  # type: ignore
