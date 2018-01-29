import datetime
import typing

import networkx  # type: ignore

from d3m_metadata import metadata as metadata_module

__all__ = ('Graph', 'DiGraph')

# TODO(eriq): MultiGraph, MultiDiGraph

G = typing.TypeVar('G', bound='Graph')
DG = typing.TypeVar('DG', bound='DiGraph')

class Graph(networkx.Graph):
    """
    Extended `networkx.Graph` with the ``metadata`` attribute.

    Parameters
    ----------
    data : networkx.Graph
        An optional exisiting graph to copy nodes/edges from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the graph.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the graph.
    """

    @property
    def _constructor(self) -> type:
        return Graph

    def __init__(self, data: networkx.Graph = None, metadata: typing.Dict[str, typing.Any] = None,
                 *, timestamp: datetime.datetime = None) -> None:
        networkx.Graph.__init__(self, data)
        self.metadata = metadata_module.DataMetadata(metadata, for_value=self, timestamp=timestamp)

    def __finalize__(self: G, other: typing.Any, method: str = None, **kwargs: typing.Any) -> G:
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

        if isinstance(obj, Graph):
            # TODO: We could adapt (if this is after a slice) or copy existing metadata?
            self.metadata: metadata_module.DataMetadata = obj.metadata.clear(for_value=self)
        else:
            self.metadata = metadata_module.DataMetadata(for_value=self)

        return self

class DiGraph(networkx.DiGraph):
    """
    Extended `networkx.DiGraph` with the ``metadata`` attribute.

    Parameters
    ----------
    data : networkx.DiGraph
        An optional exisiting graph to copy nodes/edges from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the graph.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the graph.
    """

    @property
    def _constructor(self) -> type:
        return DiGraph

    def __init__(self, data: networkx.DiGraph = None, metadata: typing.Dict[str, typing.Any] = None,
                 *, timestamp: datetime.datetime = None) -> None:
        networkx.DiGraph.__init__(self, data)
        self.metadata = metadata_module.DataMetadata(metadata, for_value=self, timestamp=timestamp)

    def __finalize__(self: DG, other: typing.Any, method: str = None, **kwargs: typing.Any) -> DG:
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

        if isinstance(obj, DiGraph):
            # TODO: We could adapt (if this is after a slice) or copy existing metadata?
            self.metadata: metadata_module.DataMetadata = obj.metadata.clear(for_value=self)
        else:
            self.metadata = metadata_module.DataMetadata(for_value=self)

        return self

typing.Sequence.register(networkx.Graph)  # type: ignore
typing.Sequence.register(networkx.DiGraph)  # type: ignore
