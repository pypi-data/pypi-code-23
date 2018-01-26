import typing

import networkx  # type: ignore
from pytypes import type_util  # type: ignore

from . import container

__all__ = ('Data', 'Container',)

# Open an issue if these standard types are too restrictive for you,
# but the idea is that callers should know in advance which data types
# are being passed in and out of primitives to be able to implement
# their introspection, serialization, and so on.

# A type representing all standard data types. Data types are those which
# can be contained inside container types.
Data = typing.Union[
    'Container',
    str, bytes, bool, float, int, dict, None,
    networkx.classes.graph.Graph, networkx.classes.digraph.DiGraph,
    networkx.classes.multigraph.MultiGraph, networkx.classes.multidigraph.MultiDiGraph,
]

# A type representing all standard container types.
Container = typing.Union[
    container.ndarray, container.matrix, container.DataFrame,
    container.SparseDataFrame, container.List[Data], container.Dataset,
]

type_util.resolve_fw_decl(Data)
type_util.resolve_fw_decl(Container)
