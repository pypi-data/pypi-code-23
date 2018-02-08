import imp
from os.path import splitext, basename, exists
from glob import glob
from typing import Union

from argus_cli import arguments
from argus_cli.helpers.collections import ImmutableDeepDict
from argus_cli.helpers.log import log
from argus_cli.helpers.formatting import to_caterpillar_case, to_camel_case

#: Contains all plugins and their functions
_plugins = ImmutableDeepDict()

#: The API that plugins will interact with
api = None


def _get_or_set_plugin(name: Union[tuple, str]) -> dict:
    """Get's a plugin. If it doesn't exist it registers it"""
    new_plugin = {}

    plugin = _plugins.setdefault(name, new_plugin)
    if plugin is new_plugin:
        arguments.register_plugin(name)

    return plugin


def _add_command(func: callable, plugin: dict, command_name: str) -> dict:
    """Adds a command to a plugin

    :param func: The function to add
    :param plugin: The plugin to add the function to
    :param command_name: The name of the function
    :raises NameError: If a command already has the same name
    """
    import inspect
    # Only raise this error if the plugin is a different module
    if command_name in plugin and id(func) != id(plugin[command_name]):
        raise NameError(
            "Command '%s' already registered by %s (#%s). Cannot re-assign to %s (#%s)" %
            (command_name,
             inspect.getsourcefile(plugin[command_name]),
             str(id(plugin[command_name])),
             inspect.getsourcefile(func),
             str(id(func.__module__)))
        )

    plugin[command_name] = func

    return plugin


def register_command(alias: str = None, extending: Union[tuple, str] = None) -> callable:
    """Decorator used to register commands to a plugin

    :param alias: If the user wants a custom name on the plugin
    :param extending: A existing plugin to extend
    """
    def decorate(func):
        if extending:
            plugin_name = (extending,) if isinstance(extending, str) else extending
        else:
            plugin_name = (func.__module__,)
        plugin_name = tuple(map(to_caterpillar_case, plugin_name))
        command_name = to_caterpillar_case(alias or func.__name__)

        plugin = _get_or_set_plugin(plugin_name)
        _add_command(func, plugin, command_name)
        arguments.register_command(plugin_name, command_name)

        return func

    return decorate


def register_command_metadata(plugin_name: tuple, command_name: str) -> None:
    """Registers the commands metadata

    Wraps the function with the same name in arguments.
    This is because this module contains the actual function to parse.

    :param plugin_name: The name of the plugin
    :param command_name: The name of the function
    """
    arguments.register_command_metadata(plugin_name, command_name, _plugins[plugin_name][command_name])


def get_plugin_modules(locations: list) -> list:
    """Loads plugins from default plugin location and user defined plugin location,
    and attempts to load them as python modules. 
    
    Directories can be loaded, provided they are python packages, i.e containing an __init__.py file. 
    If a plugin is defined as a Python package with an __init__.py file, this file must export
    all functions decorated with `@register_command`, since these will be registered on import, and
    only the __init__.py will be initially imported.
     
    NOTE: Renames plugins to common unix command naming scheme

    :param list locations: Folder with plunspgins
    :rtype: list
    :returns: A list of python files with paths
    """
    modules = []

    for path in locations:
        log.info("Loading plugins from %s..." % path)

        if not exists(path):
            log.warning("Plugin directory does not exist: %s" % path)
            continue

        # Load plugins that dont start with __ (__pycache__, __init__, __main__, etc)
        # and force the paths to the filenames
        for plugin in map(basename, glob("%s/[!__]*" % path)):
            log.debug("Extracting plugin metadata from: %s" % plugin)

            # Get the file without file extension
            module_name, file_ending = splitext(plugin)

            if file_ending and not file_ending.startswith(".py"):
                continue

            try:
                # Explicitly show the return types, to avoid confusion:
                file_reference, path_to_file, file_information = imp.find_module("%s" % module_name, [path])
            except ImportError:
                log.critical("Could not load module: %s (%s)" % (module_name, path))
                continue

            log.info("Loaded plugin %s" % to_caterpillar_case(module_name))
            modules.append({
                "name": to_caterpillar_case(module_name),
                "info": (file_reference, path_to_file, file_information)
            })

    return modules


def load_plugin_module(plugin: dict) -> bool:
    """Loads a plugin

    :param dict plugin: A dict with the module name and info
    :returns: True if module was successfully loaded
    :rtype: bool
    """
    log.debug("Loading plugin: %s" % plugin["name"])

    try:
        imp.load_module(plugin["name"], *plugin["info"])
    except Exception:
        log.exception("Error while loading plugin module:")
        return False
    finally:
        if plugin["info"][0]:
            plugin["info"][0].close()

    return True


def run_command(plugin_name: tuple, command: str, arguments: dict = None) -> None:
    """Runs the specified command

    :param plugin_name: The plugin(module) to source the command from
    :param command: The command to run
    :param arguments: Arguments to pass to the function
    :returns: Anything the command returns
    """

    command = _plugins[plugin_name][command]
    if arguments:
        formatted_arguments = { to_camel_case(key): value for key, value in arguments.items() if value is not None }
        log.info("Running command \"%s %s\" with arguments: %s" % (plugin_name, command, formatted_arguments))
        return command(**formatted_arguments)
    else:
        return command()
