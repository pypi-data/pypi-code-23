from argus_api.argus import load

from pprint import pprint
from argus_cli.helpers.log import log
from argus_cli import plugin, __version__
from argus_cli.arguments import get_command_arguments, get_plugin_arguments
from argus_cli.plugin import run_command, load_plugin_module, get_plugin_modules, register_command_metadata
from argus_cli.settings import settings


def main():
    """Used to launch the application"""

    plugin.api = load()
    plugins = get_plugin_modules(settings["cli"]["plugins"])
    log.info("Loading plugins...")
    for plug in plugins:
        load_plugin_module(plug)

    plugin_name, command_name = get_plugin_arguments()
    register_command_metadata(plugin_name, command_name)

    arguments = get_command_arguments()
    results = run_command(plugin_name, command_name, arguments)

    # If the command returns truthy values, print them out:
    if results:
        pprint(results, indent=2)
