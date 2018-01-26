import datetime
import typing

from .. import metadata as metadata_module

__all__ = ('List',)

# We see "List" as immutable for the purpose of inputs and outputs and this is why covariance is
# a reasonable choice here. Callers should make "List" immutable before passing it as inputs.
# See: PEP 484 and 483 for more details about immutability and covariance
# See: https://github.com/Stewori/pytypes/issues/21
# See: https://gitlab.com/datadrivendiscovery/metadata/issues/1
T = typing.TypeVar('T', covariant=True)
L = typing.TypeVar('L', bound='List')


class List(typing.List[T]):
    """
    Extended Python standard `typing.List` with the ``metadata`` attribute.

    You can provide a type of elements. One way is as a subclass::

        class IntList(List[int]):
            ...

        l = IntList(...)

    Another is inline::

        l = List[int](...)

    If you do not provide a type, type is assumed to be `typing.Any`.

    You should use only standard data and container types as its elements.

    Metadata attribute is immutable, so if you ``update`` it, you should reassign it back::

        l.metadata = l.metadata.update(...)

    `List` is mutable, but this can introduce issues during runtime if a primitive
    modifies its inputs directly. Callers of primitives are encouraged
    to make it immutable to assure such behavior is detected/prevented,
    and primitives should copy inputs to a mutable `List` before modifying it.

    Parameters
    ----------
    iterable : Iterable
        Optional initial values for the list.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the list.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the list.
    """

    def __init__(self, iterable: typing.Iterable = (), metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        """
        Constructor with additional optional ``metadata`` argument which serves
        as initial top-level metadata for the ``metadata`` attribute.
        """

        super().__init__(iterable)

        if isinstance(iterable, List):
            # TODO: We could copy and merge with "metadata"?
            self.metadata: metadata_module.DataMetadata = iterable.metadata.clear(for_value=self, source=source, timestamp=timestamp)

            if metadata is not None:
                self.metadata = self.metadata.update((), metadata, source=source, timestamp=timestamp)
        else:
            self.metadata = metadata_module.DataMetadata(metadata, for_value=self, source=source, timestamp=timestamp)

    def copy(self: L) -> L:
        return type(self)(iterable=self)

    @typing.overload  # type: ignore
    def __getitem__(self, i: int) -> T:
        ...

    def __getitem__(self: L, s: slice) -> L:  # type: ignore
        if isinstance(s, slice):
            lst = type(self)(iterable=super().__getitem__(s))
            # TODO: We could do a slice in metadata as well?
            #       Update dimensions. Slice per-element metadata.
            lst.metadata = self.metadata.clear(for_value=lst)
            return lst
        else:
            return super().__getitem__(s)

    def __add__(self: L, x: typing.List[T]) -> L:
        lst = type(self)(iterable=super().__add__(x))
        # TODO: We could do add in metadata as well?
        #       Update dimensions. Maybe x is List and has metadata.
        #       What to do if both have conflicting ALL_ELEMENTS metadata?
        lst.metadata = self.metadata.clear(for_value=lst)
        return lst

    def __iadd__(self: L, x: typing.Iterable[T]) -> L:
        super().__iadd__(x)
        # TODO: We could do add in metadata as well?
        #       Update dimensions. Maybe x is List and has metadata.
        #       What to do if both have conflicting ALL_ELEMENTS metadata?
        return self

    def __mul__(self: L, n: int) -> L:
        lst = type(self)(iterable=super().__mul__(n))
        # TODO: We could do multiply in metadata as well?
        #       Update dimensions. Multiplicate per-element metadata.
        lst.metadata = self.metadata.clear(for_value=lst)
        return lst

    def __rmul__(self: L, n: int) -> L:
        lst = type(self)(iterable=super().__rmul__(n))
        # TODO: We could do multiply in metadata as well?
        #       Update dimensions. Multiplicate per-element metadata.
        lst.metadata = self.metadata.clear(for_value=lst)
        return lst
