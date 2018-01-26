import collections
import copy
import datetime
import enum
import json
import inspect
import os.path
import re
import sys
import types
import typing
from urllib import parse as url_parse

import frozendict  # type: ignore
import jsonschema  # type: ignore
import numpy  # type: ignore
from pytypes import type_util  # type: ignore

from . import hyperparams as hyperparams_module, utils

__all__ = (
    'ALL_ELEMENTS', 'DataMetadata', 'PrimitiveMetadata', 'CONTAINER_SCHEMA_VERSION',
    'DATA_SCHEMA_VERSION', 'PRIMITIVE_SCHEMA_VERSION', 'PrimitiveMethodKind',
    'PrimitiveArgumentKind', 'PrimitiveInstallationType', 'PrimitiveAlgorithmType',
    'PrimitiveFamily', 'PrimitivePrecondition', 'PrimitiveEffects', 'ForeignKeyType',
)


class ALL_ELEMENTS_TYPE:
    __slots__ = ()

    def __repr__(self) -> str:
        return 'ALL_ELEMENTS'


ALL_ELEMENTS = ALL_ELEMENTS_TYPE()


COMMIT_HASH_REGEX = re.compile(r'^[0-9a-f]{40}$')


class RefResolverNoRemote(jsonschema.RefResolver):
    def resolve_remote(self, uri: str) -> typing.Any:
        raise NotImplementedError("Remote resolving disabled: {uri}".format(uri=uri))


def enum_validator(validator, enums, instance, schema):  # type: ignore
    if isinstance(instance, utils.Enum):
        instance = instance.name

    yield from jsonschema.Draft4Validator.VALIDATORS['enum'](validator, enums, instance, schema)


class Draft4Validator(jsonschema.Draft4Validator):
    """
    JSON schema validator with the following extensions:

    * Support for type "type" which succeeds if the value is a a Python type.
    * If a value is an instance of Python enumeration, its name is checked against JSON
      schema enumeration, instead of the vaule itself.

    When converting to a proper JSON these values validated under extensions should be
    converted to a stringified values (stringified Python type or enumeration's name),
    but which will then not validate anymore against the JSON schema.
    """

    VALIDATORS = dict(jsonschema.Draft4Validator.VALIDATORS, **{
        'enum': enum_validator,
    })

    def is_type(self, instance: typing.Any, type: type) -> bool:
        if type == 'type':
            return utils.is_type(instance)
        elif type == 'string' and isinstance(instance, utils.Enum):
            return True
        else:
            return super().is_type(instance, type)


SCHEMAS_PATH = os.path.join(os.path.dirname(__file__), 'schemas', 'v0')

with open(os.path.join(SCHEMAS_PATH, 'definitions.json'), 'r') as schema_file:
    DEFINITIONS_JSON = json.load(schema_file)


def load_schema_validators() -> typing.List[Draft4Validator]:
    validators = []

    for schema_filename in ('container.json', 'data.json', 'primitive.json'):
        with open(os.path.join(SCHEMAS_PATH, schema_filename), 'r') as schema_file:
            schema_json = json.load(schema_file)

        Draft4Validator.check_schema(schema_json)

        validator = Draft4Validator(
            schema=schema_json,
            types=dict(Draft4Validator.DEFAULT_TYPES, **{
                'array': (list, tuple, set),
                'object': (dict, frozendict.frozendict, frozendict.FrozenOrderedDict),
            }),
            resolver=RefResolverNoRemote(schema_json['id'], schema_json, {
                'https://metadata.datadrivendiscovery.org/schemas/v0/definitions.json': DEFINITIONS_JSON,
            }),
            format_checker=jsonschema.draft4_format_checker,
        )

        validators.append(validator)

    return validators


CONTAINER_SCHEMA_VALIDATOR, DATA_SCHEMA_VALIDATOR, PRIMITIVE_SCHEMA_VALIDATOR = load_schema_validators()

CONTAINER_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/primitive.json'
DATA_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/primitive.json'
PRIMITIVE_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/primitive.json'

PrimitiveMethodKind = utils.create_enum_from_json_schema_enum(
    'PrimitiveMethodKind', DEFINITIONS_JSON,
    'definitions.primitive_code.properties.instance_methods.additionalProperties.properties.kind.oneOf[*].enum[*]',
)
PrimitiveArgumentKind = utils.create_enum_from_json_schema_enum(
    'PrimitiveArgumentKind', DEFINITIONS_JSON,
    'definitions.primitive_code.properties.arguments.additionalProperties.properties.kind.oneOf[*].enum[*]',
)
PrimitiveInstallationType = utils.create_enum_from_json_schema_enum(
    'PrimitiveInstallationType', DEFINITIONS_JSON,
    'definitions.installation.items.anyOf[*].properties.type.enum[*]',
)
PrimitiveAlgorithmType = utils.create_enum_from_json_schema_enum(
    'PrimitiveAlgorithmType', DEFINITIONS_JSON,
    'definitions.algorithm_types.items.anyOf[*].enum[*]',
)
PrimitiveFamily = utils.create_enum_from_json_schema_enum(
    'PrimitiveFamily', DEFINITIONS_JSON,
    'definitions.primitive_family.oneOf[*].enum[*]',
)
PrimitivePrecondition = utils.create_enum_from_json_schema_enum(
    'PrimitivePrecondition', DEFINITIONS_JSON,
    'definitions.preconditions.items.anyOf[*].enum[*]',
)
PrimitiveEffects = utils.create_enum_from_json_schema_enum(
    'PrimitiveEffects', DEFINITIONS_JSON,
    'definitions.effects.items.anyOf[*].enum[*]',
)

ForeignKeyType = utils.create_enum_from_json_schema_enum(
    'ForeignKeyType', DEFINITIONS_JSON,
    'definitions.foreign_key.oneOf[*].properties.type.enum[*]',
)


T = typing.TypeVar('T', bound='Metadata')
D = typing.TypeVar('D', bound='DataMetadata')
P = typing.TypeVar('P', bound='PrimitiveMetadata')
SimpleSelectorSegment = typing.Union[int, str]
SelectorSegment = typing.Union[SimpleSelectorSegment, ALL_ELEMENTS_TYPE]
# A list or tuple of integers, strings, or ALL_ELEMENTS.
Selector = typing.Union[typing.List[SelectorSegment], typing.Tuple[SelectorSegment, ...]]


class MetadataJsonEncoder(json.JSONEncoder):
    """
    JSON encoder with the following extensions:

    * Frozen dict is encoded as a dict.
    * Python types are encoded into strings describing them.
    * Python enumerations are encoded into their string names.
    """

    def default(self, o: typing.Any) -> typing.Any:
        if isinstance(o, frozendict.frozendict):
            return dict(o)
        if isinstance(o, frozendict.FrozenOrderedDict):
            return collections.OrderedDict(o)
        if utils.is_type(o):
            return type_util.type_str(o, assumed_globals={}, update_assumed_globals=False)
        if isinstance(o, utils.Enum):
            return o.name
        if o is ALL_ELEMENTS:
            return '__ALL_ELEMENTS__'
        # For encoding numpy.int64. numpy.float64 already works.
        if isinstance(o, numpy.integer):
            return int(o)

        return super().default(o)


def to_json_structure(obj: typing.Any) -> typing.Any:
    # TODO: Is there a better way to trigger a run of MetadataJsonEncoder recursively without going to a string?
    return json.loads(json.dumps(obj, cls=MetadataJsonEncoder))


class LogEntry(typing.NamedTuple):
    selector: Selector
    metadata: typing.Dict[str, typing.Any]
    source: typing.Optional[datetime.datetime]
    timestamp: typing.Any


class LogClear(typing.NamedTuple):
    source: typing.Optional[datetime.datetime]
    timestamp: typing.Any


class MetadataEntry:
    def __init__(self) -> None:
        self.elements: typing.Dict[SimpleSelectorSegment, MetadataEntry] = {}
        self.all_elements: MetadataEntry = None
        self.metadata: frozendict.FrozenOrderedDict = frozendict.FrozenOrderedDict()


class Metadata:
    """
    A basic class to be used as a value for `metadata` attribute
    on values passed between primitives.

    Instances are immutable.

    Parameters
    ----------
    metadata : Dict[str, Any]
        Optional initial metadata for the top-level of the value.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.
    """

    def __init__(self, metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        self._metadata_log: typing.Tuple[typing.Union[LogEntry, LogClear], ...] = ()
        self._current_metadata = MetadataEntry()

        self._hash: int = None

        if metadata is not None:
            self._update_in_place((), metadata, self._metadata_log, self._current_metadata, source, timestamp)

    def update(self: T, selector: Selector, metadata: typing.Dict[str, typing.Any], *, source: typing.Any = None, timestamp: datetime.datetime = None) -> T:
        """
        Updates metadata with new ``metadata`` for data pointed to with ``selector``.

        It returns a copy of this metadata object with new metadata applied.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            A selector pointing to data.
        metadata : Dict
            A map of keys and values with metadata.
        source : primitive or Any
            A source of this metadata change. Can be an instance of a primitive or any other relevant
            source reference.
        timestamp : datetime
            A timestamp of this metadata change.

        Returns
        -------
        Metadata
            Updated metadata.
        """

        cls = type(self)

        new_metadata = cls()

        new_metadata._update_in_place(selector, metadata, self._metadata_log, self._current_metadata, source, timestamp)

        return new_metadata

    def clear(self: T, metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> T:
        """
        Clears all metadata and returns a new empty (or initialized with ``metadata``) object.

        This is almost the same as creating a new metadata instance from scratch, but it keeps the link with
        the previous metadata object and preserves the history. Access to history is not yet exposed through
        an API but in the future this can help with provenance of data going through a pipeline.

        Parameters
        ----------
        metadata : Dict[str, Any]
            Optional new initial metadata for the top-level of the value.
        source : primitive or Any
            A source of this metadata change. Can be an instance of a primitive or any other relevant
            source reference.
        timestamp : datetime
            A timestamp of this metadata change.

        Returns
        -------
        Metadata
            Updated metadata.
        """

        cls = type(self)

        new_metadata = cls()

        new_metadata_log_clear = LogClear(source=source, timestamp=timestamp)

        new_metadata._metadata_log = self._metadata_log + (new_metadata_log_clear,)

        if metadata is not None:
            new_metadata._update_in_place((), metadata, new_metadata._metadata_log, new_metadata._current_metadata, source, timestamp)

        return new_metadata

    # TODO: If particular metadata (dict) gets empty ({}), we should remove it from its parent metadata entry.
    def _update_in_place(self, selector: Selector, metadata: typing.Dict[str, typing.Any], parent_metadata_log: typing.Tuple[typing.Union[LogEntry, LogClear], ...],
                         parent_current_metadata: MetadataEntry, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        """
        This method exist only for internal purposes and you should never ever call this to update metadata from outside.
        """

        self.check_selector(selector)

        metadata = utils.make_immutable_copy(metadata)

        if not isinstance(metadata, frozendict.FrozenOrderedDict):
            raise TypeError("Metadata should be a dict.")

        if timestamp is None:
            timestamp = datetime.datetime.now(datetime.timezone.utc)

        new_metadata_log_entry = LogEntry(selector=selector, metadata=metadata, source=source, timestamp=timestamp)

        self._metadata_log = parent_metadata_log + (new_metadata_log_entry,)
        self._current_metadata = self._update(selector, parent_current_metadata, metadata)

    # TODO: Using ALL_ELEMENTS should return only values which really hold for all elements.
    #       Or, a different special selector could be provided for that.
    # TODO: Provide additional special selectors.
    #       For example, to get which elements have metadata which does not hold for all elements.
    # TODO: Allow querying only a subset of metadata (not the whole dict).
    def query(self, selector: Selector) -> frozendict.FrozenOrderedDict:
        """
        Returns metadata for data pointed to with ``selector``.

        When querying using ALL_ELEMENTS means only metadata which has been set using ALL_ELEMENTS
        is returned.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            A selector to query metadata for.

        Returns
        -------
        frozendict.FrozenOrderedDict
            Metadata at a given selector.
        """

        self.check_selector(selector)

        # TODO: Maybe cache results? LRU?
        return self._query(selector, self._current_metadata)

    def _query(self, selector: Selector, metadata_entry: typing.Optional[MetadataEntry]) -> frozendict.FrozenOrderedDict:
        if metadata_entry is None:
            return frozendict.FrozenOrderedDict()
        if len(selector) == 0:
            return self._merge_metadata(frozendict.FrozenOrderedDict(), metadata_entry.metadata, True)

        segment, selector_rest = selector[0], selector[1:]

        all_elements_metadata = self._query(selector_rest, metadata_entry.all_elements)
        if segment is ALL_ELEMENTS:
            metadata = all_elements_metadata
        elif segment in metadata_entry.elements:
            segment = typing.cast(SimpleSelectorSegment, segment)
            metadata = self._query(selector_rest, metadata_entry.elements[segment])
            metadata = self._merge_metadata(all_elements_metadata, metadata, True)
        else:
            metadata = all_elements_metadata

        return metadata

    def _update(self, selector: Selector, metadata_entry: typing.Optional[MetadataEntry], metadata: frozendict.FrozenOrderedDict) -> MetadataEntry:
        if metadata_entry is None:
            new_metadata_entry = MetadataEntry()
        else:
            new_metadata_entry = copy.copy(metadata_entry)

        if len(selector) == 0:
            # We do not remove None values here because we have to keep them around to know
            # which values we have to remove when merging with all elements metadata.
            new_metadata_entry.metadata = self._merge_metadata(new_metadata_entry.metadata, metadata, False)
            return new_metadata_entry

        segment, selector_rest = selector[0], selector[1:]

        if metadata_entry is not None:
            # We will be changing elements, so if we copied metadata_entry, we have to copy elements as well.
            new_metadata_entry.elements = copy.copy(new_metadata_entry.elements)

        if segment is ALL_ELEMENTS:
            new_metadata_entry.all_elements = self._update(selector_rest, new_metadata_entry.all_elements, metadata)

            # Fields on direct elements have precedence over fields on ALL_ELEMENTS, but we want the last
            # call to update to take precedence. So all fields found in metadata just set on ALL_ELEMENTS
            # are removed from all metadata on direct elements.
            for element_segment, element_metadata_entry in new_metadata_entry.elements.items():
                new_metadata_entry.elements[element_segment] = self._prune(selector_rest, element_metadata_entry, metadata)

        else:
            segment = typing.cast(SimpleSelectorSegment, segment)
            new_metadata_entry.elements[segment] = self._update(selector_rest, new_metadata_entry.elements.get(segment, None), metadata)

        return new_metadata_entry

    def _merge_metadata(self, metadata1: frozendict.FrozenOrderedDict, metadata2: frozendict.FrozenOrderedDict, remove_none: bool = False) -> frozendict.FrozenOrderedDict:
        """
        Merges all fields from ``metadata`` on top of ``metadata1``, recursively.

        If ``remove_none`` is set to ``True``, then all fields with ``None`` values are removed,
        instead of copied over.

        Only dicts are merged recursively, arrays are not.
        """

        # Copy so that we can mutate.
        metadata = collections.OrderedDict(metadata1)

        for name, value in metadata2.items():
            if name in metadata:
                if remove_none and value is None:
                    del metadata[name]
                elif isinstance(metadata[name], frozendict.FrozenOrderedDict) and isinstance(value, frozendict.FrozenOrderedDict):
                    metadata[name] = self._merge_metadata(metadata[name], value, remove_none)
                else:
                    metadata[name] = value
            else:
                if remove_none and value is None:
                    pass
                # We have to recurse only if we have to remove None values.
                elif remove_none and isinstance(value, frozendict.FrozenOrderedDict):
                    metadata[name] = self._merge_metadata(frozendict.FrozenOrderedDict(), value, remove_none)
                else:
                    metadata[name] = value

        return frozendict.FrozenOrderedDict(metadata)

    def _prune(self, selector: Selector, metadata_entry: typing.Optional[MetadataEntry], metadata: frozendict.FrozenOrderedDict) -> MetadataEntry:
        new_metadata_entry = copy.copy(metadata_entry)

        if len(selector) == 0:
            new_metadata_entry.metadata = self._prune_metadata(new_metadata_entry.metadata, metadata)
            return new_metadata_entry

        segment, selector_rest = selector[0], selector[1:]

        new_metadata_entry.elements = copy.copy(new_metadata_entry.elements)

        if segment is ALL_ELEMENTS:
            new_metadata_entry.all_elements = self._prune(selector_rest, new_metadata_entry.all_elements, metadata)

            for element_segment, element_metadata_entry in new_metadata_entry.elements.items():
                new_metadata_entry.elements[element_segment] = self._prune(selector_rest, element_metadata_entry, metadata)

        elif segment in new_metadata_entry.elements:
            segment = typing.cast(SimpleSelectorSegment, segment)
            new_metadata_entry.elements[segment] = self._prune(selector_rest, new_metadata_entry.elements[segment], metadata)

        return new_metadata_entry

    def _prune_metadata(self, metadata1: frozendict.FrozenOrderedDict, metadata2: frozendict.FrozenOrderedDict) -> frozendict.FrozenOrderedDict:
        """
        Removes all fields which are found in ``metadata2`` from ``metadata1``, recursively.

        Values of ``metadata2`` do not matter, except if they are a dict, in which case
        removal is done recursively.
        """

        # Copy so that we can mutate.
        metadata = collections.OrderedDict(metadata1)

        for name, value in metadata2.items():
            if name not in metadata:
                continue

            if isinstance(metadata[name], frozendict.FrozenOrderedDict) and isinstance(value, frozendict.FrozenOrderedDict):
                metadata[name] = self._prune_metadata(metadata[name], value)
            else:
                del metadata[name]

        return frozendict.FrozenOrderedDict(metadata)

    @classmethod
    def check_selector(cls, selector: Selector) -> None:
        """
        Checks that a given ``selector`` is a valid selector. If ``selector`` is invalid it raises an exception.

        It checks that it is a tuple or a list and currently we require that all segments of a selector
        are strings, integers, or a special value ``ALL_ELEMENTS``.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            Selector to check.
        """

        if isinstance(selector, list):
            selector = tuple(selector)
        if not isinstance(selector, tuple):
            raise TypeError("Selector is not a tuple or a list.")

        path = []
        for segment in selector:
            path.append(segment)

            if not isinstance(segment, (str, int)) and segment is not ALL_ELEMENTS:
                raise TypeError("'{segment}' at {path} is not a str, int, or ALL_ELEMENTS.".format(segment=segment, path=path))

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._metadata_log)

        return self._hash

    def get_elements(self, selector: Selector) -> typing.List[SelectorSegment]:
        """
        Returns a list of element names which exists under a selector, if any.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            A selector to return elements under.

        Returns
        -------
        List[int or str or ALL_ELEMENTS]
            List of element names.
        """

        self.check_selector(selector)

        return self._get_elements(selector, self._current_metadata)

    def _get_elements(self, selector: Selector, metadata_entry: typing.Optional[MetadataEntry]) -> typing.List[SelectorSegment]:
        if metadata_entry is None:
            return []
        if len(selector) == 0:
            if metadata_entry.all_elements is not None:
                all_elements: typing.List[SelectorSegment] = [ALL_ELEMENTS]
            else:
                all_elements = []
            return all_elements + list(metadata_entry.elements.keys())

        segment, selector_rest = selector[0], selector[1:]

        all_elements_elements = self._get_elements(selector_rest, metadata_entry.all_elements)
        if segment is ALL_ELEMENTS:
            elements = all_elements_elements
        elif segment in metadata_entry.elements:
            segment = typing.cast(SimpleSelectorSegment, segment)
            elements = self._get_elements(selector_rest, metadata_entry.elements[segment])
            elements = list(set(all_elements_elements + elements))
        else:
            elements = all_elements_elements

        return elements

    def to_json(self) -> typing.List[typing.Dict[str, typing.Dict]]:
        """
        Converts metadata to a JSON-compatible structure.

        Returns
        -------
        List[Dict]
            A JSON-compatible list of dicts.
        """

        return self._to_json([], self._current_metadata)

    def _to_json(self, selector: Selector, metadata_entry: typing.Optional[MetadataEntry]) -> typing.List[typing.Dict[str, typing.Dict]]:
        output = []

        selector = typing.cast(typing.List[SelectorSegment], selector)

        metadata = to_json_structure(metadata_entry.metadata)
        if metadata:
            output.append({
                'selector': to_json_structure(selector),
                'metadata': metadata,
            })

        if metadata_entry.all_elements is not None:
            output += self._to_json(selector + [ALL_ELEMENTS], metadata_entry.all_elements)

        for element_segment, element_metadata_entry in metadata_entry.elements.items():
            output += self._to_json(selector + [element_segment], element_metadata_entry)

        return output

    def pretty_print(self, selector: Selector = None, handle: typing.TextIO = None, _level: int = 0) -> None:
        """
        Pretty-prints metadata to ``handle``, or `sys.stdout` if not specified.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            A selector to start pretty-printing at.
        handle : TextIO
            A handle to pretty-print to. Default is `sys.stdout`.
        """

        if selector is None:
            selector = []

        if handle is None:
            handle = sys.stdout

        self.check_selector(selector)

        selector = list(selector)

        if 'selector' in inspect.getfullargspec(self.query).args:
            query = self.query
        else:
            def query(selector: Selector) -> frozendict.FrozenOrderedDict:
                return self.query()  # type: ignore

        indent = ' ' * _level

        handle.write('{indent}Selector:\n{indent} {selector}\n'.format(indent=indent, selector=tuple(selector)))

        handle.write('{indent}Metadata:\n'.format(indent=indent))
        for line in json.dumps(query(selector=selector), indent=1, cls=MetadataJsonEncoder).splitlines():
            handle.write('{indent} {line}\n'.format(indent=indent, line=line))

        elements = self.get_elements(selector)

        if not elements:
            return

        if ALL_ELEMENTS in elements:
            handle.write('{indent}All elements:\n'.format(indent=indent))
            self.pretty_print(selector + [ALL_ELEMENTS], handle=handle, _level=_level + 1)

        first_element = True
        for element in elements:
            if element is ALL_ELEMENTS:
                continue

            if first_element:
                handle.write('{indent}Elements:\n'.format(indent=indent))
                first_element = False

            self.pretty_print(selector + [element], handle=handle, _level=_level + 1)


# TODO: Should we automatically extract things from the value which we can?
#       Like dimensions and structural types.
class DataMetadata(Metadata):
    """
    A class for metadata for data values.

    It checks all updates against container and data schemas, and if ``for_value`` is
    set, against value itself as well.

    Parameters
    ----------
    metadata : Dict[str, Any]
        Optional initial metadata for the top-level of the value.
    for_value : Any
        Optional value associated with metadata to check updates against to
        make sure they point to data which exists.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.
    """

    def __init__(self, metadata: typing.Dict[str, typing.Any] = None, for_value: typing.Any = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        super().__init__(metadata=metadata, source=source, timestamp=timestamp)

        self.for_value = for_value

        if metadata is not None:
            updated_metadata = self.query(selector=())

            CONTAINER_SCHEMA_VALIDATOR.validate(updated_metadata)

    def update(self: D, selector: Selector, metadata: typing.Dict[str, typing.Any], *, for_value: typing.Any = None, source: typing.Any = None, timestamp: datetime.datetime = None) -> D:
        """
        Updates metadata with new ``metadata`` for data pointed to with ``selector``.

        It returns a copy of this metadata object with new metadata applied.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            A selector pointing to data.
        metadata : Dict
            A map of keys and values with metadata.
        for_value : Any
            Optional value associated with metadata to check updates against to
            make sure they point to data which exists.
            It replaces any previous set value associated with metadata.
        source : primitive or Any
            A source of this metadata change. Can be an instance of a primitive or any other relevant
            source reference.
        timestamp : datetime
            A timestamp of this metadata change.

        Returns
        -------
        DataMetadata
            Updated metadata.
        """

        if for_value is None:
            for_value = self.for_value

        self.check_selector(selector, for_value)

        new_metadata = super().update(selector=selector, metadata=metadata, source=source, timestamp=timestamp)

        new_metadata.for_value = for_value

        updated_metadata = new_metadata.query(selector=selector)

        if len(selector) == 0:
            CONTAINER_SCHEMA_VALIDATOR.validate(updated_metadata)
        else:
            DATA_SCHEMA_VALIDATOR.validate(updated_metadata)

        return new_metadata

    def clear(self: D, metadata: typing.Dict[str, typing.Any] = None, *, for_value: typing.Any = None, source: typing.Any = None, timestamp: datetime.datetime = None) -> D:
        """
        Clears all metadata and returns a new empty (or initialized with ``metadata``) object.

        This is almost the same as creating a new metadata instance from scratch, but it keeps the link with
        the previous metadata object and preserves the history. Access to history is not yet exposed through
        an API but in the future this can help with provenance of data going through a pipeline.

        Parameters
        ----------
        metadata : Dict[str, Any]
            Optional new initial metadata for the top-level of the value.
        for_value : Any
            Optional value associated with metadata to check updates against to
            make sure they point to data which exists.
        source : primitive or Any
            A source of this metadata change. Can be an instance of a primitive or any other relevant
            source reference.
        timestamp : datetime
            A timestamp of this metadata change.

        Returns
        -------
        DataMetadata
            Updated metadata.
        """

        if for_value is None:
            for_value = self.for_value

        new_metadata = super().clear(metadata=metadata, source=source, timestamp=timestamp)

        new_metadata.for_value = for_value

        if metadata is not None:
            updated_metadata = new_metadata.query(selector=())

            CONTAINER_SCHEMA_VALIDATOR.validate(updated_metadata)

        return new_metadata

    def check(self, for_value: typing.Any) -> None:
        """
        Checks that all metadata has a corresponding data in ``for_value``.
        If not it raises an exception.

        Parameters
        ----------
        for_value : Any
            Value to check against.
        """

        self._check(self._current_metadata, for_value, [])

    def _check(self, metadata_entry: MetadataEntry, for_value: typing.Any, path: typing.List[SimpleSelectorSegment]) -> None:
        if metadata_entry.all_elements is not None:
            try:
                # We should be able to at least compute length at this dimension
                # (to signal that it is a sequence or a map).
                len(for_value)
            except Exception as error:
                raise ValueError("ALL_ELEMENTS set but dimension missing at {path}.".format(path=path)) from error

        for element_segment, element_metadata_entry in metadata_entry.elements.items():
            try:
                element_value = for_value[element_segment]
            except Exception as error:
                raise ValueError("'{element_segment}' at {path} cannot be resolved.".format(element_segment=element_segment, path=path)) from error

            self._check(element_metadata_entry, element_value, path + [element_segment])

    @classmethod
    def check_selector(cls, selector: Selector, for_value: typing.Any = None) -> None:
        """
        Checks that a given ``selector`` is a valid selector. If ``selector`` is invalid it raises an exception.

        It checks that it is a tuple or a list and currently we require that all segments of a selector
        are strings, integers, or a special value ``ALL_ELEMENTS``.

        If ``for_value`` is provided, it also tries to resolve the ``selector`` against the value
        to assure that the selector is really pointing to data which exists.

        Parameters
        ----------
        selector : Tuple(str or int or ALL_ELEMENTS)
            Selector to check.
        for_value : Any
            Value to check against.
        """

        super().check_selector(selector=selector)

        if for_value is not None:
            cls._check_for_value(selector, for_value, [])

    @classmethod
    def _check_for_value(cls, selector: Selector, for_value: typing.Any, path: typing.List[SelectorSegment]) -> None:
        if not selector:
            return

        segment, selector_rest = selector[0], selector[1:]

        if segment is ALL_ELEMENTS:
            for element_value in for_value:
                cls._check_for_value(selector_rest, element_value, path + [segment])
        else:
            try:
                element_value = for_value[segment]
            except Exception as error:
                raise ValueError("'{segment}' at {path} cannot be resolved.".format(segment=segment, path=path)) from error

            cls._check_for_value(selector_rest, element_value, path + [segment])


def _get_package(value: typing.Any) -> types.ModuleType:
    if '.' in value.__module__:
        package_name = value.__module__.split('.')[0]
    else:
        package_name = value.__module__
    return sys.modules[package_name]


def _get_full_name(value: typing.Any) -> str:
    return '{module}.{name}'.format(module=value.__module__, name=value.__name__)


class PrimitiveMetadata(Metadata):
    """
    A class for metadata for primitives.

    It checks all updates against primitive schema.
    """

    def __init__(self, metadata: typing.Dict[str, typing.Any] = None) -> None:
        super().__init__(metadata=metadata)

        # We do not do validation here because provided metadata on its own is
        # probably not sufficient for validation to pass. Validation happens
        # inside "contribute_to_class" method instead.

        # "primitive" should be of PrimitiveBase here, but we do not want to
        # introduce a dependency on primitive interfaces package because it
        # would introduce a cyclic dependency between packages.
        # We validate the type at runtime in "contribute_to_class method.
        self.primitive: typing.Any = None

    # Not adhering to Liskov substitution principle: we do not have "selector" argument.
    def update(self: P, metadata: typing.Dict[str, typing.Any], *, source: typing.Any = None, timestamp: datetime.datetime = None) -> P:  # type: ignore
        new_metadata = super().update(selector=(), metadata=metadata, source=source, timestamp=timestamp)

        self._validate()

        return new_metadata

    def clear(self: P, metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> P:
        new_metadata = super().clear(metadata=metadata, source=source, timestamp=timestamp)

        new_metadata.primitive = self.primitive

        new_metadata._generate_and_update()

        return new_metadata

    # Not adhering to Liskov substitution principle: we do not have "selector" argument.
    def query(self) -> frozendict.FrozenOrderedDict:  # type: ignore
        return super().query(selector=())

    # "primitive" should be of PrimitiveBase here, but we do not want to
    # introduce a dependency on primitive interfaces package because it
    # would introduce a cyclic dependency between packages.
    # We validate the type at runtime in the method.
    def contribute_to_class(self: P, primitive: typing.Any) -> None:
        # We do not depend on primitive-interfaces package to prevent dependency
        # cycle, but if you are calling this method, you have the package installed.
        from primitive_interfaces import base

        if self.primitive is not None:
            raise ValueError("Primitive is already set to '{primitive}'.".format(primitive=self.primitive))

        if not issubclass(primitive, base.PrimitiveBase):
            raise TypeError("Primitive argument is not a subclass of PrimitiveBase.")

        self.primitive = primitive

        self._generate_and_update()

    def _validate(self) -> None:
        metadata = self.query()

        PRIMITIVE_SCHEMA_VALIDATOR.validate(metadata)

        self._validate_installation(metadata)

    def _generate_and_update(self) -> None:
        generated_metadata = self._generate_metadata_for_primitive()

        self._update_in_place((), generated_metadata, self._metadata_log, self._current_metadata)

        self._validate()

    def _validate_installation(self, metadata: frozendict.FrozenOrderedDict) -> None:
        for entry in metadata.get('installation', []):
            # We can check simply equality because metadata enumerations are equal to strings as well,
            # and "entry['type']" can be both a string or an enumeration instance.
            if entry['type'] != PrimitiveInstallationType.PIP:
                continue

            if 'package' in entry:
                if '/' in entry['package']:
                    raise ValueError("Invalid package name '{package_name}'. If you want to use an URI pointing to a package, use 'package_uri' instead.".format(
                        package_name=entry['package'],
                    ))

                continue

            if 'package_uri' not in entry:
                continue

            if entry['package_uri'].startswith('git+git@'):
                # "git+git@git.myproject.org:MyProject" format cannot be parsed with urlparse.
                raise ValueError("Only git+http and git+https URI schemes are allowed.")

            parsed_uri = url_parse.urlparse(entry['package_uri'])

            # It is not a git pip URI. For now we then do not validate it.
            if not parsed_uri.scheme.startswith('git'):
                continue

            if parsed_uri.scheme not in ['git+http', 'git+https']:
                raise ValueError("Only git+http and git+https URI schemes are allowed.")

            if '@' not in parsed_uri.path:
                raise ValueError("Package URI does not include a commit hash: {package_uri}".format(package_uri=entry['package_uri']))

            path, commit_hash = parsed_uri.path.rsplit('@', 1)

            if not COMMIT_HASH_REGEX.match(commit_hash):
                raise ValueError("Package URI does not include a commit hash: {package_uri}".format(package_uri=entry['package_uri']))

            if not parsed_uri.fragment:
                raise ValueError("Package URI does not include a '#egg=package_name' URI suffix.")

            parsed_fragment = url_parse.parse_qs(parsed_uri.fragment, strict_parsing=True)

            if 'egg' not in parsed_fragment:
                raise ValueError("Package URI does not include a '#egg=package_name' URI suffix.")

    def _generate_metadata_for_primitive(self) -> typing.Dict[str, typing.Any]:
        # We do not depend on primitive-interfaces package to prevent dependency
        # cycle, but if you are calling this method, you have the package installed.
        import primitive_interfaces
        from primitive_interfaces import base

        type_arguments = self._get_type_arguments()
        class_attributes = self._get_class_attributes()
        hyperparams_class = typing.cast(typing.Type[hyperparams_module.Hyperparams], type_arguments[base.Hyperparams])
        arguments, instance_methods = self._get_arguments_and_methods(hyperparams_class, type_arguments)
        hyperparams = self._get_hyperparams(hyperparams_class)
        class_methods = self._get_class_methods(type_arguments)
        instance_attributes = self._get_instance_attributes(hyperparams_class, class_methods, instance_methods, class_attributes)
        params = self._get_params(type_arguments)

        # Sanity check.
        hyperparams_keys = set(hyperparams.keys())
        # We can check simply equality because metadata enumerations are equal to strings as well,
        # and "argument['kind']" can be both a string or an enumeration instance.
        non_hyperparameter_arguments_keys = {name for name, argument in arguments.items() if argument['kind'] != PrimitiveArgumentKind.HYPERPARAMETER}
        overlapping_keys = hyperparams_keys & non_hyperparameter_arguments_keys
        if len(overlapping_keys):
            raise ValueError("Hyper-paramater names are overlapping with non-hyperparameter argument names: {overlapping_keys}".format(overlapping_keys=overlapping_keys))

        primitive_code = {
            # We have to convert parameters to their names because JSON schema supports only strings for keys.
            'class_type_arguments': {parameter.__name__: argument for parameter, argument in type_arguments.items()},
            'interfaces_version': primitive_interfaces.__version__,
            'interfaces': self._get_interfaces(),
            'hyperparams': hyperparams,
            'arguments': arguments,
            'class_methods': class_methods,
            'instance_methods': instance_methods,
            'class_attributes': class_attributes,
            'instance_attributes': instance_attributes,
        }

        if params is not None:
            primitive_code['params'] = params

        result = {
            'schema': PRIMITIVE_SCHEMA_VERSION,
            'original_python_path': '{module}.{class_name}'.format(
                module=self.primitive.__module__,
                class_name=self.primitive.__name__,
            ),
            'primitive_code': primitive_code,
            'structural_type': self.primitive,
        }

        description = inspect.cleandoc(getattr(self.primitive, '__doc__', None) or '') or None
        if description is not None:
            result['description'] = description

        return result

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    def _get_type_arguments(self) -> typing.Dict[type, type]:
        # We do not depend on primitive-interfaces package to prevent dependency
        # cycle, but if you are calling this method, you have the package installed.
        from primitive_interfaces import base

        # This call also catches if type parameter has been overridden with a new type variable.
        # This means that we for free get to make sure type parameters from the base class stay
        # as they are expected to be. It also fetches them recursively, so one cannot hide a
        # type parameter (but can fix it to a fixed type instead of leaving it open for a
        # subclass to choose it).
        type_arguments = utils.get_type_arguments(self.primitive)

        for parameter, argument in type_arguments.items():
            # Params type argument is optional and can be set to None.
            if parameter == base.Params and issubclass(argument, type(None)):
                continue

            if not utils.is_subclass(argument, parameter):
                raise TypeError("Type parameter '{name}' has type '{type}' and not an expected type: {expected}".format(
                    name=parameter.__name__, type=argument, expected=parameter.__bound__,  # type: ignore
                ))

        return type_arguments

    def _resolve_type(self, obj: type, type_arguments: typing.Dict[type, type]) -> type:
        if obj in type_arguments:
            return type_arguments[obj]
        else:
            return obj

    def _get_interfaces(self) -> typing.Tuple[str, ...]:
        # We do not depend on primitive-interfaces package to prevent dependency
        # cycle, but if you are calling this method, you have the package installed.
        import primitive_interfaces

        mro = [parent for parent in inspect.getmro(self.primitive) if _get_package(parent) is primitive_interfaces]

        interfaces: typing.List[str] = []
        for parent in mro:
            interface = _get_full_name(parent)
            # Remove package name.
            interface = '.'.join(interface.split('.')[1:])
            if interface not in interfaces:
                interfaces.append(interface)

        if not len(interfaces):
            raise TypeError("The primitive does not implement a standard interface.")

        return tuple(interfaces)

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    def _get_params(self, type_arguments: typing.Dict[type, type]) -> typing.Optional[typing.Dict[str, type]]:
        # We do not depend on primitive-interfaces package to prevent dependency
        # cycle, but if you are calling this method, you have the package installed.
        from primitive_interfaces import base

        params = type_arguments.get(base.Params, type(None))

        if issubclass(params, type(None)):
            return None

        return params.__params_items__  # type: ignore

    def _get_hyperparams(self, hyperparams_class: 'typing.Type[hyperparams_module.Hyperparams]') -> typing.Dict[str, typing.Dict]:
        return hyperparams_class.to_json()

    def _get_class_attributes(self) -> typing.Dict[str, type]:
        result = {}

        for attribute_name, attribute in inspect.getmembers(self.primitive):
            if attribute_name.startswith('_'):
                continue

            if utils.is_class_method_on_class(attribute) or utils.is_instance_method_on_class(attribute):
                continue

            result[attribute_name] = type(attribute)

        result_keys = set(result.keys())
        expected_result_keys = set(EXPECTED_CLASS_ATTRIBUTES.keys())

        missing = expected_result_keys - result_keys
        if len(missing):
            raise ValueError("Not all expected public class attributes exist: {missing}".format(missing=missing))

        extra = result_keys - expected_result_keys
        if len(extra):
            raise ValueError("Additional unexpected public class attributes exist, consider making them private by prefixing them with '_': {extra}".format(extra=extra))

        for attribute_name, attribute in result.items():
            if not issubclass(attribute, EXPECTED_CLASS_ATTRIBUTES[attribute_name]):
                raise TypeError("Class attribute '{attribute_name}' does not have an expected type.".format(attribute_name=attribute_name))

        return result

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    def _get_arguments_and_methods(self, hyperparams_class: 'typing.Type[hyperparams_module.Hyperparams]', type_arguments: typing.Dict[type, type]) \
            -> typing.Tuple[typing.Dict[str, typing.Dict], typing.Dict[str, typing.Dict]]:
        # We do not depend on primitive-interfaces package to prevent dependency
        # cycle, but if you are calling this method, you have the package installed.
        from primitive_interfaces import base

        from . import types as types_module

        arguments: typing.Dict[str, typing.Dict] = {}
        methods: typing.Dict[str, typing.Dict] = {}

        for method_name, method in inspect.getmembers(self.primitive):
            if method_name.startswith('_') and method_name != '__init__':
                continue

            if not utils.is_instance_method_on_class(method):
                continue

            # To make get_type_hints find method's module while the primitive's
            # module is still being defined (and this method was indirectly called
            # from primitive's metaclass).
            method.im_class = self.primitive

            type_hints = type_util.get_type_hints(method)

            if not type_hints:
                raise TypeError("Cannot get types for method '{method_name}'.".format(method_name=method_name))

            if 'return' not in type_hints:
                raise TypeError("Method '{method_name}' is missing a type for the return value.".format(method_name=method_name))

            if method_name.startswith('produce_') or method_name == 'produce':
                method_kind = PrimitiveMethodKind.PRODUCE
            elif method_name.startswith('produce'):
                raise ValueError("Produce method should start with 'produce_' and not be '{method_name}'.".format(method_name=method_name))
            else:
                method_kind = PrimitiveMethodKind.OTHER

            method_arguments = []

            # We skip the first argument (self).
            for argument_name, argument in list(inspect.signature(method).parameters.items())[1:]:
                if argument.kind != inspect.Parameter.KEYWORD_ONLY:
                    raise TypeError("Method '{method_name}' has a non-keyword argument '{argument_name}'.".format(method_name=method_name, argument_name=argument_name))

                has_default = argument.default is not inspect.Parameter.empty

                if argument_name.startswith('_'):
                    if not has_default:
                        raise TypeError("Method '{method_name}' has a non-optional private argument '{argument_name}'.".format(method_name=method_name, argument_name=argument_name))

                    continue

                if argument_name not in type_hints:
                    raise TypeError("Method '{method_name}' is missing a type for argument '{argument_name}'.".format(method_name=method_name, argument_name=argument_name))

                argument_type = self._resolve_type(type_hints[argument_name], type_arguments)

                standard_argument_description = typing.cast(
                    typing.Dict,
                    STANDARD_RUNTIME_ARGUMENTS.get(argument_name, None) or STANDARD_RUNTIME_ARGUMENTS.get(argument_name, None),
                )
                if standard_argument_description is not None:
                    try:
                        expected_type = self._get_argument_type(standard_argument_description, type_arguments)
                    except KeyError:
                        raise TypeError("Method '{method_name}' has an argument '{argument_name}' for which an expected type cannot be determined. Is a type parameter missing?".format(
                            method_name=method_name, argument_name=argument_name,
                        ))

                    # Types have to match here exactly. This is what class type arguments are for.
                    if argument_type != expected_type:
                        raise TypeError("Method '{method_name}' has an argument '{argument_name}' with type '{argument_type}' and not an expected type: {expected_type}".format(
                            method_name=method_name, argument_name=argument_name,
                            argument_type=argument_type, expected_type=expected_type,
                        ))

                    if 'default' in standard_argument_description:
                        if not has_default:
                            raise ValueError("Method '{method_name}' has an argument '{argument_name}' which does not have a default value, but it should.".format(
                                method_name=method_name, argument_name=argument_name,
                            ))

                        if argument.default != standard_argument_description['default']:
                            raise ValueError("Method '{method_name}' has an argument '{argument_name}' with a different default value: {argument_default} != {expected_default}.".format(
                                method_name=method_name, argument_name=argument_name,
                                argument_default=argument.default, expected_default=standard_argument_description['default'],
                            ))

                    else:
                        if has_default:
                            raise ValueError("Method '{method_name}' has an argument '{argument_name}' which has a default value, but it should not.".format(
                                method_name=method_name, argument_name=argument_name,
                            ))

                    if argument_name in STANDARD_RUNTIME_ARGUMENTS:
                        argument_kind = PrimitiveArgumentKind.RUNTIME
                    else:
                        assert argument_name in STANDARD_PIPELINE_ARGUMENTS, "argument_name not in STANDARD_PIPELINE_ARGUMENTS"
                        argument_kind = PrimitiveArgumentKind.PIPELINE

                elif argument_name in hyperparams_class.configuration:
                    # Types have to match here exactly.
                    if argument_type != hyperparams_class.configuration[argument_name].structural_type:
                        raise ValueError("Method '{method_name}' has an argument '{argument_name}' overriding a hyper-parameter with a different type: {argument_type} != {hyperparameter_type}.".format(  # noqa
                            method_name=method_name, argument_name=argument_name,
                            argument_type=argument_type, hyperparameter_type=hyperparams_class.configuration[argument_name].structural_type,
                        ))

                    # Arguments overriding a hyper-parameter should not have a default value and caller should pass a value in.
                    if has_default:
                        raise ValueError("Method '{method_name}' has an argument '{argument_name}' overriding a hyper-parameter which has a default value, but it should not.".format(
                            method_name=method_name, argument_name=argument_name,
                        ))

                    argument_kind = PrimitiveArgumentKind.HYPERPARAMETER

                else:
                    # Any other argument should be something the rest of the pipeline can provide:
                    # a container value, data value, or another primitive.
                    expected_type = typing.Union[types_module.Container, types_module.Data, base.PrimitiveBase]

                    if not utils.is_subclass(argument_type, expected_type):
                        raise TypeError("Method '{method_name}' has an argument '{argument_name}' with type '{argument_type}' and not an expected type: {expected_type}".format(
                            method_name=method_name, argument_name=argument_name,
                            argument_type=argument_type, expected_type=expected_type
                        ))

                    # It should not have a default. Otherwise it is easy to satisfy the argument
                    # (just never connect anything to it in the pipeline).
                    if has_default:
                        raise ValueError("Method '{method_name}' has an argument '{argument_name}' which has a default value, but it should not.".format(
                            method_name=method_name, argument_name=argument_name,
                        ))

                    argument_kind = PrimitiveArgumentKind.PIPELINE

                method_arguments.append(argument_name)

                if has_default:
                    # This is meant mostly so that for numerical arguments one can have an
                    # easy record of what were defaults in place. For more complicated values
                    # caller probably want to pass them in anyway.
                    argument_default = utils.to_json_value(argument.default)
                else:
                    argument_default = None

                if argument_name in arguments:
                    if argument_type != arguments[argument_name]['type']:
                        raise ValueError("Method '{method_name}' has an argument '{argument_name}' which does not match a type of a previous argument with the same name: {argument_type} != {previous_type}".format(  # noqa
                            method_name=method_name, argument_name=argument_name,
                            argument_type=argument_type, previous_type=arguments[argument_name]['type'],
                        ))

                    # This should hold because it depends only on the argument name.
                    assert argument_kind == arguments[argument_name]['kind'], "argument_kind mismatch"

                    # This works because we do not store "None" value directly but as a string using "utils.to_json_value".
                    if argument_default != arguments[argument_name].get('default', None):
                        raise ValueError("Method '{method_name}' has an argument '{argument_name}' which does not have the same default value as a previous argument with the same name: {argument_default} != {previous_default}".format(  # noqa
                            method_name=method_name, argument_name=argument_name,
                            argument_default=argument_default,
                            previous_default=arguments[argument_name].get('default', None),
                        ))

                else:
                    arguments[argument_name] = {
                        'type': argument_type,
                        'kind': argument_kind,
                    }

                    if has_default:
                        arguments[argument_name]['default'] = argument_default

            methods[method_name] = {
                'kind': method_kind,
                'arguments': method_arguments,
                'returns': self._resolve_type(type_hints['return'], type_arguments),
            }

            description = inspect.cleandoc(getattr(method, '__doc__', None) or '') or None
            if description is not None:
                methods[method_name]['description'] = description

        return arguments, methods

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    def _get_argument_type(self, argument_description: typing.Dict[str, typing.Any], type_arguments: typing.Dict[type, type]) -> type:
        if 'get_type' in argument_description:
            return argument_description['get_type'](type_arguments)
        else:
            return argument_description['type']

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    def _get_class_methods(self, type_arguments: typing.Dict[type, type]) -> typing.Dict[str, typing.Dict]:
        methods: typing.Dict[str, typing.Dict] = {}

        for method_name, method in inspect.getmembers(self.primitive):
            if method_name.startswith('_'):
                continue

            if not utils.is_class_method_on_class(method):
                continue

            type_hints = type_util.get_type_hints(method)

            if not type_hints:
                raise TypeError("Cannot get types for method '{method_name}'.".format(method_name=method_name))

            if 'return' not in type_hints:
                raise TypeError("Method '{method_name}' is missing a type for the return value.".format(method_name=method_name))

            method_arguments = {}

            for argument_name, argument in inspect.signature(method).parameters.items():
                if argument.kind != inspect.Parameter.KEYWORD_ONLY:
                    raise TypeError("Method '{method_name}' has a non-keyword argument '{argument_name}'.".format(method_name=method_name, argument_name=argument_name))

                has_default = argument.default is not inspect.Parameter.empty

                if argument_name.startswith('_'):
                    if not has_default:
                        raise TypeError("Method '{method_name}' has a non-optional private argument '{argument_name}'.".format(method_name=method_name, argument_name=argument_name))

                    continue

                if argument_name not in type_hints:
                    raise TypeError("Method '{method_name}' is missing a type for argument '{argument_name}'.".format(method_name=method_name, argument_name=argument_name))

                argument_type = self._resolve_type(type_hints[argument_name], type_arguments)

                argument_description = {
                    'type': argument_type,
                }

                if has_default:
                    # This is meant mostly so that for numerical arguments one can have an
                    # easy record of what were defaults in place. For more complicated values
                    # caller probably want to pass them in anyway.
                    argument_description['default'] = utils.to_json_value(argument.default)

                method_arguments[argument_name] = argument_description

            methods[method_name] = {
                'arguments': method_arguments,
                'returns': self._resolve_type(type_hints['return'], type_arguments),
            }

            description = inspect.cleandoc(getattr(method, '__doc__', None) or '') or None
            if description is not None:
                methods[method_name]['description'] = description

        return methods

    def _get_docker_containers(self) -> typing.Tuple[str, ...]:
        installation = self.query().get('installation', [])

        containers: typing.List[str] = []

        for entry in installation:
            # We can check simply equality because metadata enumerations are equal to strings as well,
            # and "entry['type']" can be both a string or an enumeration instance.
            if entry.get('type', None) != PrimitiveInstallationType.DOCKER:
                continue

            key = entry.get('key', None)
            if key:
                containers.append(key)

        containers_set = set(containers)
        if len(containers_set) != len(containers):
            for key in containers_set:
                containers.remove(key)
            raise TypeError("Same Docker image key reused across multiple installation entries: {extra_keys}".format(extra_keys=containers))

        return tuple(containers)

    def _get_instance_attributes(self, hyperparams_class: 'typing.Type[hyperparams_module.Hyperparams]', class_methods: typing.Dict[str, typing.Dict],
                                 instance_methods: typing.Dict[str, typing.Dict], class_attributes: typing.Dict[str, type]) -> typing.Dict[str, type]:
        hyperparams = hyperparams_class.defaults()
        random_seed = 42
        # Dummy Docker container addresses. Primitive's constructor should
        # be thin and not yet do anything with them.
        docker_containers = {key: 'localhost' for key in self._get_docker_containers()}

        # We checked before this that the signature matches the one in the base class,
        # so we know that we can call it like this.
        primitive = self.primitive(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)

        expected_attributes = {
            'hyperparams': hyperparams,
            'random_seed': random_seed,
            'docker_containers': docker_containers,
        }

        attributes = []

        for attribute_name, attribute in inspect.getmembers(primitive):
            if attribute_name.startswith('_'):
                continue

            if attribute_name in class_methods:
                continue

            if attribute_name in instance_methods:
                continue

            if attribute_name in class_attributes:
                continue

            if attribute_name in expected_attributes:
                if attribute is not expected_attributes[attribute_name] or attribute != expected_attributes[attribute_name]:
                    raise ValueError("Primitive instance attribute '{attribute_name}' is not equal to a given constructor argument.".format(attribute_name=attribute_name))

            attributes.append(attribute_name)

        attributes_keys = set(attributes)
        expected_attributes_keys = set(expected_attributes.keys())

        missing = expected_attributes_keys - attributes_keys
        if len(missing):
            raise ValueError("Not all expected public instance attributes exist: {missing}".format(missing=missing))

        extra = attributes_keys - expected_attributes_keys
        if len(extra):
            raise ValueError("Additional unexpected public instance attributes exist, consider making them private by prefixing them with '_': {extra}".format(extra=extra))

        # Primitive instance attributes are standardized and fixed.
        return {
            'hyperparams': hyperparams_module.Hyperparams,
            'random_seed': int,
            'docker_containers': typing.Dict[str, str],
        }

    # Not adhering to Liskov substitution principle: we are not returning a list.
    def to_json(self) -> typing.Dict[str, typing.Dict]:  # type: ignore
        """
        Converts primitive's metadata to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        return super().to_json()[0]['metadata']


EXPECTED_CLASS_ATTRIBUTES = {
    'metadata': PrimitiveMetadata,
}


def _get_inputs(type_arguments: typing.Dict[type, type]) -> type:
    # We do not depend on primitive-interfaces package to prevent dependency
    # cycle, but if you are calling this method, you have the package installed.
    from primitive_interfaces import base

    return type_arguments[base.Inputs]


def _get_outputs(type_arguments: typing.Dict[type, type]) -> type:
    # We do not depend on primitive-interfaces package to prevent dependency
    # cycle, but if you are calling this method, you have the package installed.
    from primitive_interfaces import base

    return type_arguments[base.Outputs]


def _get_input_labels(type_arguments: typing.Dict[type, type]) -> type:
    # We do not depend on primitive-interfaces package to prevent dependency
    # cycle, but if you are calling this method, you have the package installed.
    from primitive_interfaces import distance

    return type_arguments[distance.InputLabels]


# Arguments which can be fulfilled by other primitives in a pipeline.
STANDARD_PIPELINE_ARGUMENTS = {
    'inputs': {
        'get_type': _get_inputs,
    },
    'outputs': {
        'get_type': _get_outputs,
    },
    'input_labels': {
        'get_type': _get_input_labels,
    },
}


def _get_hyperparams(type_arguments: typing.Dict[type, type]) -> type:
    # We do not depend on primitive-interfaces package to prevent dependency
    # cycle, but if you are calling this method, you have the package installed.
    from primitive_interfaces import base

    return type_arguments[base.Hyperparams]


def _get_params(type_arguments: typing.Dict[type, type]) -> type:
    # We do not depend on primitive-interfaces package to prevent dependency
    # cycle, but if you are calling this method, you have the package installed.
    from primitive_interfaces import base

    return type_arguments[base.Params]


def _get_gradient_outputs(type_arguments: typing.Dict[type, type]) -> type:
    # We do not depend on primitive-interfaces package to prevent dependency
    # cycle, but if you are calling this method, you have the package installed.
    from primitive_interfaces import base

    return base.Gradients[type_arguments[base.Outputs]]  # type: ignore


# Arguments which are meaningful only for a runtime executing a pipeline.
STANDARD_RUNTIME_ARGUMENTS = {
    'hyperparams': {
        'get_type': _get_hyperparams,
    },
    'random_seed': {
        'type': int,
        'default': 0,
    },
    'docker_containers': {
        'type': typing.Optional[typing.Dict[str, str]],
        'default': None,
    },
    'timeout': {
        'type': typing.Optional[float],
        'default': None,
    },
    'iterations': {
        'type': typing.Optional[int],
        'default': None,
    },
    'params': {
        'get_type': _get_params,
    },
    'num_samples': {
        'type': int,
        'default': 1,
    },
    'gradient_outputs': {
        'get_type': _get_gradient_outputs,
    },
    'fine_tune':  {
        'type': bool,
        'default': False,
    },
    'fine_tune_learning_rate': {
        'type': float,
        'default': 0.00001,
    },
    'fine_tune_weight_decay': {
        'type': float,
        'default': 0.00001,
    },
    'temperature': {
        'type': float,
        'default': 0,
    },
}
