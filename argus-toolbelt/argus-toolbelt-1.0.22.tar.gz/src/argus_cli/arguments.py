import collections
import inspect
import re
import sys

import argparse
from argparse import ArgumentParser
from pydoc import locate

from argus_cli.helpers.collections import ImmutableDeepDict
from argus_cli.helpers.log import log
from argus_cli.helpers.formatting import to_caterpillar_case

#: The key of the plugin argument
_PLUGIN_ARGUMENT = "_plugins"
# Storage location for the parsers
_PLUGIN_PARSER = "_parser"
_PLUGIN_SUBPARSER = "_subparser"

# Regexes used to check for arguments
#: Checks if the line is argument metadata
_ARGUMENT_META_REGEX = re.compile(r":(?:param|alias)")
#: Gets data from the parameter
_PARAM_REGEX = re.compile(r":param (?P<name>[*\w]+): (?P<doc>.*)")
#: Gets aliases for parameter
_ALIAS_REGEX = re.compile(r":alias\s+(?P<name>[*\w]+):\s+(?P<aliases>.*)")
#: Gets data from the parameter
_TYPE_PARAM_REGEX = re.compile(r":param (?P<argument_type>[*\w]+) (?P<name>[*\w]+): (?P<doc>.*)")


class PluginParserContainer(object):
    """A container that handles plugin parsers

    Each node in the dict has three objects.
        _subparsers: The _SubParserAction object (that you add parsers to)
        _parser: The actual parser. This is just used for testing
        Everything else: Commands and sub-plugins
    """
    class _StorePlugin(argparse._SubParsersAction):
        """Makes plugin subparsers store the used subparser in one list."""
        def __call__(self, parser, namespace, values, option_string=None):
            super().__call__(parser, namespace, values, option_string)

            # Values will be all arguments after this plugin.
            # Just get the name of this plugin.
            values = values[0]
            if not hasattr(namespace, _PLUGIN_ARGUMENT):
                setattr(namespace, _PLUGIN_ARGUMENT, [values])
            else:
                getattr(namespace, _PLUGIN_ARGUMENT).insert(0, values)

    def __init__(self, main_parser):
        self._dict = ImmutableDeepDict()
        self._plugin_parser = main_parser.add_subparsers(
            action=self._StorePlugin,
            help="Which plugin to use",
        )

    def __str__(self):
        return str(self._dict)

    def _add_parser(self, plugin: tuple) -> ArgumentParser:
        """Adds a plugin's parser to the tree."""
        plugin_name = plugin[-1]
        if len(plugin) == 1:
            # This is a top level plugin
            parent_parser = self._plugin_parser
        else:
            try:
                parent_parser = self._dict[plugin[:-1]][_PLUGIN_SUBPARSER]
            except KeyError:
                # A key-error means that the parent doesn't have a parser.
                parent_parser = self._add_parser(plugin[:-1])

        new_parser = parent_parser.add_parser(plugin_name)
        new_subparser = new_parser.add_subparsers(action=self._StorePlugin)
        self._dict[plugin] = {
            _PLUGIN_PARSER: new_parser,  # Used for testing
            _PLUGIN_SUBPARSER: new_subparser
        }

        return new_subparser

    def add_parser(self, plugin: tuple) -> None:
        """Adds a parser to the container"""
        self._add_parser(plugin)

    def add_command(self, plugin: tuple, command_name: str) -> ArgumentParser:
        """Adds a command to a plugin parser"""
        plugin_container = self._dict[plugin]
        plugin_parser = plugin_container[_PLUGIN_SUBPARSER]
        plugin_container[command_name] = plugin_parser.add_parser(command_name)

        return plugin_container[command_name]

    def get_plugin(self, plugin: tuple):
        """Gets a plugin parser"""
        return self._dict[plugin]

    def get_command(self, plugin: tuple, command_name: str):
        """Gets a command from a plugin"""
        return self._dict[plugin][command_name]


#: The parser to rule them all!
_ROOT_PARSER = ArgumentParser(prog="Argus Toolbelt")
#: Parsers that handles a plugins commands
_PARSERS = PluginParserContainer(_ROOT_PARSER)


def _parse_type(parameter_type, argument: dict) -> dict:
    """Parses a parameter's type

    :param parameter_type: The type of the parameter
    :param argument: The argument to modify
    :returns: Modified argument
    """
    if isinstance(parameter_type, list):
        if any(isinstance(element, collections.Sequence) and not isinstance(element, str) for element in parameter_type):
            raise ValueError("A list of choices can not have a nested iterable object.")
        argument["choices"] = parameter_type
    elif inspect.isclass(parameter_type) and issubclass(parameter_type, (list, tuple)):
        # When a user specifies a "list" input it's not a instance of list yet.
        # Hence here we use issubclass() instead.
        argument["nargs"] = '*'
    elif isinstance(parameter_type, collections.Callable):
        argument["type"] = parameter_type
    else:
        raise ValueError("Non-supported parameter type")

    return argument


def _parse_parameters(function: callable) -> dict:
    """Parses a functions parameters.

    :param function: The function to parse
    :returns: All arguments, ready to pass to argparse
    """
    arguments = collections.OrderedDict()
    signature = inspect.signature(function)

    log.debug("%s arguments: %s" % (function.__name__, signature))

    for name, parameter in signature.parameters.items():
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            # **kwargs Have to be defined in docstrings
            log.debug("**%s argument ignored. kwargs are added from the docstring." % name)
            continue

        arguments[name] = {"names": [to_caterpillar_case(name)]}

        if parameter.default is not parameter.empty:
            arguments[name]["required"] = False
            arguments[name]["default"] = parameter.default

        if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
            arguments[name]["required"] = False
            arguments[name]["nargs"] = "*"

        if parameter.annotation is not parameter.empty:
            arguments[name] = _parse_type(parameter.annotation, arguments[name])

    log.debug("%s: Registered commands from signature:\n\t%s" % (function.__name__, arguments))
    return arguments


def _parse_docstring(function: callable, parsed: dict) -> dict:
    """Parses a function's docstring for more info about it and it's parameters.

    :param function: The function to parse
    :param parsed: Existing arguments for the function
    :return: Short description, Long description and more argument info
    """
    # Escape all % { and } so argparse doesnt crash when trying to format the string
    lines = function.__doc__.replace("{", "{{").replace("}", "}}").replace("%", "%%").split("\n", 1)

    help_text = lines[0].strip()

    if len(lines) <= 1:
        parsed["help"] = help_text
        return parsed

    description = lines[1]

    arguments_part = None
    match = _ARGUMENT_META_REGEX.search(description)
    if match:
        arguments_part = description[match.start():]
        description = description[:match.start()].strip()
    else:
        description = description.strip()

    arguments = parsed["arguments"]

    if arguments_part:
        for argument_type, name, doc in _TYPE_PARAM_REGEX.findall(arguments_part):
            if name not in arguments:
                arguments[name] = {"names": [to_caterpillar_case(name)]}
                arguments[name]["required"] = False
            arguments[name]["help"] = doc
            if "type" not in arguments[name]:
                arguments[name] = _parse_type(locate(argument_type), arguments[name])
            else:
                log.warning("Attempted to set type in both function annotation and docstring for argument %s" % name)

        for name, doc in _PARAM_REGEX.findall(arguments_part):
            if name not in arguments:
                arguments[name] = {"names": [to_caterpillar_case(name)]}
                arguments[name]["required"] = False
            arguments[name]["help"] = doc

        for name, aliases in _ALIAS_REGEX.findall(arguments_part):
            if name not in arguments:
                raise NameError("%s is not an argument. An argument has to exist to be aliased." % name)
            for alias in aliases.split(","):
                arguments[name]["names"].append(to_caterpillar_case(alias.strip()))

    log.debug(
        "%s: Finished parsing function metadata:\n\t%s\n\t%s\n\t%s"
        % (function.__name__, help_text, description, arguments)
    )

    parsed["arguments"] = arguments
    parsed["help"] = help_text
    parsed["description"] = description
    return parsed


def _parse_function(function: callable) -> dict:
    """Parses a functions parameters and help-text from its docstring and annotations.

    :param function: A function
    :return: The description and arguments (in order) for the function
    """
    parsed = {}

    log.debug("Parsing arguments and docstring for %s..." % function.__name__)

    parsed["arguments"] = _parse_parameters(function)

    if not function.__doc__:
        return parsed

    parsed = _parse_docstring(function, parsed)

    return parsed


def register_plugin(plugin_sequence: tuple) -> None:
    """Creates a parser for a plugin

    :param plugin_sequence: The plugin sequence
    :raises KeyError: If the plugin already exists
    """
    log.debug("Registering parser for plugin \"%s\"" % (plugin_sequence,))
    _PARSERS.add_parser(plugin_sequence)


def register_command(plugin_sequence: tuple, command_name: str) -> None:
    """Registers a command towards a plugin.

    :param plugin_sequence: The name of the plugin that the function belongs to
    :param command_name: The name of the function
    """
    log.debug("Registering parser for command \"%s\" in plugin \"%s\"" % (command_name, "/".join(plugin_sequence)))
    _PARSERS.add_command(plugin_sequence, command_name)


def register_command_metadata(plugin_sequence: tuple, command_name: str, function: callable) -> None:
    """Registers the function metadata to a parser

    Registering the metadata is done at a later point to not do unnecessary operations with _parse_function().
    A single call to _parse_function() takes quite some time, so it's better to do it JIT.

    :param plugin_sequence: The name of the plugin
    :param command_name: The name of the command
    :param function: The function to parse metadata from
    """
    log.debug("Registering metadata for \"%s\" on plugin \"%s\"" % (command_name, "/".join(plugin_sequence)))

    command = _PARSERS.get_command(plugin_sequence, command_name)
    metadata = _parse_function(function)

    if "help" in metadata and metadata["help"]:
        command.help = metadata["help"]
    if "description" in metadata and metadata["description"]:
        command.description = metadata["description"]

    for options in metadata["arguments"].values():
        if "required" in options and not options["required"]:
            names = []
            for name in options.pop("names"):
                prefix = "-" if len(name) is 1 else "--"
                names.append(prefix + name)
        else:
            names = options.pop("names")

        command.add_argument(*names, **options)


def get_plugin_arguments() -> tuple:
    """Only parse the plugin arguments.

    Plugin arguments are the <plugin> and <command> part of the CLI.
    If we do not do it like this help-messages for commands would be catched in here,
    and thus we wouldn't get a proper help message for commands.

    :returns: Plugin and command name
    """
    def error_or_help(parser):
        if any(keyword in sys.argv for keyword in ("--help", "-h")):
            parser.print_help()
            parser.exit()
        parser.error("Not enough arguments")

    log.debug("Parsing plugin arguments")

    base_args = [arg for arg in sys.argv[1:] if arg != "--help"]
    args = vars(_ROOT_PARSER.parse_known_args(base_args)[0])

    if _PLUGIN_ARGUMENT not in args:
        error_or_help(_ROOT_PARSER)

    plugin_name = tuple(args[_PLUGIN_ARGUMENT][:-1])
    command_name = args[_PLUGIN_ARGUMENT][-1]

    try:
        parser = _PARSERS.get_command(plugin_name, command_name)
    except KeyError:
        parser = _PARSERS.get_plugin(command_name)  # If there is just one argument it will end up here

    if isinstance(parser, dict):
        error_or_help(parser[_PLUGIN_PARSER])

    return plugin_name, command_name


def get_command_arguments() -> dict:
    """Gets the command arguments.

    See get_plugin_arguments() for why we do it like this.

    :returns: Command arguments
    """
    log.debug("Parsing command arguments")

    parsed = vars(_ROOT_PARSER.parse_args())
    # Remove plugin arguments as they aren't necessary for the command arguments
    parsed.pop(_PLUGIN_ARGUMENT)

    return parsed
