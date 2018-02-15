import re

from datetime import datetime
from enum import Enum, IntEnum

from base64 import b64encode
from base64 import b64decode

from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import fromstring


class DecofError(Exception):
    """A generic DeCoF error."""
    pass


class DecofValueError(Exception):
    """A DeCoF value conversion error."""
    def __init(self, result: str, expected_type: type):
        super().__init__("Failed to convert {!r} to type '{}'".format(result, expected_type))


DecofType = Union[bool, int, float, str, bytes, tuple]
DecofMetaType = Type[DecofType]

DecofStreamType = Union[str, bytes]
DecofStreamMetaType = Type[DecofStreamType]

DecofCallback = Callable[[datetime, str, DecofType, DecofError], None]
DecofMonitoringLine = Tuple[datetime, str, Union[str, DecofError]]


class AccessLevel(IntEnum):
    """An access level of a parameter in a DeCoF system model."""
    INTERNAL = 0
    SERVICE = 1
    MAINTENANCE = 2
    NORMAL = 3
    READONLY = 4


class ParamMode(Enum):
    """An access mode of a parameter in a DeCoF system model."""
    READONLY = 1
    WRITEONLY = 2
    READWRITE = 3
    READSET = 4


class StreamType(Enum):
    """A stream type of a command in a DeCoF system model."""
    TEXT = 1
    BASE64 = 2


def access_level(access_level_str: Optional[str]) -> Optional[AccessLevel]:
    """Converts a string with a parameter access level to the corresponding type.

    Args:
        access_level_str (str): The string with the parameter access level.

    Returns:
        Optional[AccessLevel]: The type of the parameter access level.

    """

    table = {'internal':    AccessLevel.INTERNAL,
             'service':     AccessLevel.SERVICE,
             'maintenance': AccessLevel.MAINTENANCE,
             'normal':      AccessLevel.NORMAL,
             'readonly':    AccessLevel.READONLY}

    try:
        return table[access_level_str.strip().lower()]
    except (AttributeError, KeyError):
        return None


def access_mode(access_mode_str: Optional[str]) -> Optional[ParamMode]:
    """Converts a string with a parameter access mode to the corresponding type.

    Args:
        access_mode_str (str): The string with the parameter access mode.

    Returns:
        Optional[ParamMode]: The type of the parameter access mode.

    """

    table = {'readonly':  ParamMode.READONLY,
             'writeonly': ParamMode.WRITEONLY,
             'readwrite': ParamMode.READWRITE,
             'readset':   ParamMode.READSET}

    try:
        return table[access_mode_str.strip().lower()]
    except (AttributeError, KeyError):
        return None


def stream_type(stream_type_str: Optional[str]) -> Optional[StreamType]:
    """Converts a string with a command stream type to the corresponding type.

    Args:
        stream_type_str (str): The string with the command stream type.

    Returns:
        Optional[StreamType]: The type of the command stream type.

    """
    table = {'base64': StreamType.BASE64,
             'text':   StreamType.TEXT}

    try:
        return table[stream_type_str.strip().lower()]
    except (AttributeError, KeyError):
        return None


def encode_value(value: DecofType) -> str:
    """Encodes a value to a string.

    Args:
        value (DecofType): The value of the parameter.

    Returns:
        str: The encoded value.

    """
    if isinstance(value, bool):
        return '#t' if value else '#f'

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        return '"' + value + '"'

    if isinstance(value, bytes):
        return '"' + b64encode(value).decode() + '"'

    raise DecofError('Invalid type for value: {}'.format(type(value)))


def decode_value(result: str, expected_type: DecofMetaType) -> DecofType:
    """Converts a DeCoF parameter string to a Python value.

    Args:
        result (str): The string returned by the command line.
        expected_type (DecofTypeList): The expected type of the result.

    Returns:
        DecofType: The value of the command line result.

    Raises:
        DecofError: If the command line returned an error message
        DecofValueError: If the command line result couldn't be converted to the expected type.

    """
    if result.lower().startswith('error'):
        raise DecofError(result)

    try:
        if expected_type is int:
            return int(result)
    except ValueError:
        raise DecofValueError(result, int)

    try:
        if expected_type is float:
            return float(result)
    except ValueError:
        raise DecofValueError(result, float)

    if expected_type is bool:
        if result in ['#t', '#T']:
            return True
        if result in ['#f', '#F']:
            return False
        raise DecofValueError(result, bool)

    if expected_type is str:
        if not result.startswith('"') or not result.endswith('"'):
            raise DecofValueError(result, str)
        return result.strip('"')

    if expected_type is bytes:
        if result.startswith('&'):
            return b64decode(result[1:])
        if result.startswith('"') and result.endswith('"'):
            return b64decode(result[1:-1])
        raise DecofValueError(result, bytes)

    if expected_type is tuple:
        if result.startswith("'(") and result.endswith(")"):
            return tuple(result[2:-1].split(' '))
        raise DecofValueError(result, tuple)

    raise DecofError("Unexpected type while decoding a DeCoF value: '{}'".format(expected_type))


def parse_monitoring_line(line: str) -> DecofMonitoringLine:
    """Parses a monitoring line message.

    Args:
        line (str): A monitoring line message.

    Returns:
        DecofMonitoringLine: A tuple containing the timestamp, parameter name and value/exception.

    """
    datetime_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'

    if line.lower().startswith('(error: '):
        match = re.match(r"\(Error: (.*?) \((.*?) '(.*?)\) (.*?)\)\r\n", line, re.IGNORECASE)

        if match is not None:
            ls = match.groups()
            timestamp = datetime.strptime(ls[1], datetime_fmt)
            error = DecofError('Error: {} {}'.format(ls[0], ls[3]))
            return timestamp, ls[2], error
    else:
        match = re.match(r"\((.*?) '(.*?) (.*?)\)\r\n", line)

        if match is not None:
            ls = match.groups()
            timestamp = datetime.strptime(ls[0], datetime_fmt)
            return timestamp, ls[1], ls[2]

    error = DecofError('Invalid monitoring line message: {!r}'.format(line))
    return datetime.now(), '', error


class Parameter:
    """A parameter in a DeCoF system model.

    Attributes:
        name (str): The name of the parameter.
        typestr (str): The type of the parameter.
        mode (ParamMode): The access mode of the parameter.
        readlevel(AccessLevel): The required access level to read the parameter.
        writelevel(AccessLevel): The required access level to write the parameter.

    """
    def __init__(self, name: str, typestr: str, description: str, mode: ParamMode, readlevel: Optional[AccessLevel], writelevel: Optional[AccessLevel]) -> None:
        self.name = name
        self.paramtype = typestr
        self.description = description
        self.mode = mode
        self.readlevel = readlevel
        self.writelevel = writelevel


class Command:
    """A command in the DeCoF system model.

    Attributes:
        name(str): The name of the command.
        input_type(StreamType): The type of the input stream.
        output_type (StreamType): The type of the output stream.
        execlevel (AccessLevel): The required access level to execute the command.
        params (List[Tuple[str, str]]): The list of parameter names and types of the command.
        return_type (str): The type of the return value.

    """
    def __init__(self, name: str, description: str, input_type: Optional[StreamType], output_type: Optional[StreamType], execlevel: Optional[AccessLevel], params: List[Tuple[str, str]], return_type: str) -> None:
        self.name = name
        self.description = description
        self.input_type = input_type
        self.output_type = output_type
        self.execlevel = execlevel
        self.params = params
        self.return_type = return_type


class Typedef:
    """A typedef in a DeCoF system model.

    Attributes:
        name (str): The name of the typedef.
        is_atomic (bool): True if the typedef is atomic, False otherwise.

    """

    def __init__(self, name: str, is_atomic: bool) -> None:
        self.name = name
        self.is_atomic = is_atomic
        self.params = {}  # type: Dict[str, Parameter]
        self.cmds = {}  # type: Dict[str, Command]


class Module:
    """A module in a DeCoF system model.

    Attributes:
        name (str): The name of the module.

    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.params = {}  # type: Dict[str, Parameter]
        self.cmds = {}  # type: Dict[str, Command]


class SystemModel:
    """A DeCoF system model."""

    def __init__(self) -> None:
        self.name = ''
        self.typedefs = {}  # type: Dict[str, Typedef]
        self.modules = {}  # type: Dict[str, Module]

    def build_from_file(self, filename: str) -> None:
        """Loads a DeCoF system model from an XML file.

        Args:
            filename (str): The name of the XML file with the DeCoF system model.

        """
        xml = ElementTree(file=filename)
        self._build_model(xml)

    def build_from_string(self, xml_str: str) -> None:
        """Loads a DeCoF system model form a string.

        Args:
            xml_str (str): A string containing the XML description of the DeCoF system model.

        """
        xml = ElementTree(fromstring(xml_str))
        self._build_model(xml)

    def _build_model(self, xml: ElementTree) -> None:
        """Builds the system model from an XML tree.

        Args:
            xml (ElementTree): The DeCoF system model.

        """
        self._read_system(xml)
        self._read_xtypedefs(xml)
        self._read_modules(xml)

    def _read_system(self, xml: ElementTree) -> None:
        """Reads system definition from the DeCoF system model.

        Args:
            xml (ElementTree): The DeCoF system model.

        """
        self.name = xml.getroot().get('name')

    def _read_xtypedefs(self, xml: ElementTree) -> None:
        """Reads all typedefs from the DeCoF system model.

        Args:
            xml (ElementTree): The DeCoF system model.

        """
        for xtypedef in xml.iter(tag='xtypedef'):
            name = xtypedef.get('name')
            is_atomic = str(xtypedef.get('is_atomic')).lower() == 'true'
            node = Typedef(name, is_atomic)
            self._read_params(xtypedef, node, None)
            self._read_cmds(xtypedef, node)
            self.typedefs[name] = node

    def _read_modules(self, xml: ElementTree) -> None:
        """Reads all modules from the DeCoF system model.

        Args:
            xml (ElementTree): The DeCoF system model.

        """
        for mod in xml.iter(tag='module'):
            name = mod.get('name')
            node = Module(name)
            self._read_params(mod, node, AccessLevel.NORMAL)
            self._read_cmds(mod, node)
            self.modules[name] = node

    @staticmethod
    def _read_params(element: Element, node: Union[Module, Typedef], default_level: Optional[AccessLevel]) -> None:
        """Reads all parameters of a DeCoF system model node.

        Args:
            element (ElementTree): The DeCoF system model node.
            node (Node): The node in this system model.

        """
        for param in element.iter(tag='param'):
            param_name = param.get('name')
            param_type = param.get('type')
            param_mode = access_mode(param.get('mode'))
            readlevel = access_level(param.get('readlevel'))
            writelevel = access_level(param.get('writelevel'))
            if readlevel is None and param_mode != ParamMode.WRITEONLY:
                readlevel = default_level
            if writelevel is None and param_mode != ParamMode.READONLY:
                writelevel = default_level
            param_description = ''
            for desc in param.iter(tag='description'):
                param_description += desc.text
            node.params[param_name] = Parameter(param_name, param_type, param_description, param_mode, readlevel, writelevel)

    @staticmethod
    def _read_cmds(element: Element, node: Union[Module, Typedef]) -> None:
        """Reads all commands of a DeCoF system model node.

        Args:
            element (ElementTree): The DeCoF system model node.
            node (Node): The node in this system model.

        """
        for cmd in element.iter(tag='cmd'):
            cmd_name = cmd.get('name')
            cmd_in = stream_type(cmd.get('input'))
            cmd_out = stream_type(cmd.get('output'))
            execlevel = access_level(cmd.get('execlevel'))
            ret_type = None
            for ret in cmd.iter(tag='ret'):
                ret_type = ret.get('type')
            desc = ''
            for item in cmd.iter(tag='description'):
                desc += item.text
            params = []
            for arg in cmd.iter(tag='arg'):
                arg_name = arg.get('name')
                arg_type = arg.get('type')
                params.append((arg_name, arg_type))
            node.cmds[cmd_name] = Command(cmd_name, desc, cmd_in, cmd_out, execlevel, params, ret_type)
