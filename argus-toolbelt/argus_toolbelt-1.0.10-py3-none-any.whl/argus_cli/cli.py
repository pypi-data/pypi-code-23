from argus_api import ArgusAPI

from pprint import pprint
from argus_cli.helpers.log import log
from argus_cli import plugin, __version__
from argus_cli.arguments import get_command_arguments, get_plugin_arguments
from argus_cli.plugin import run_command, load_plugin_module, get_plugin_modules, register_command_metadata
from argus_cli.settings import settings


def get_api_instance(arguments):
    """Creates a instance of the API

    :param arguments: Arguments
    :return: ArgusAPI instance
    """
    log.info("Getting an API instance...")

    api_args = {}
    if "api_key" in arguments:
        api_args["api_key"] = arguments["api_key"]
    elif "username" in arguments:
        # FIXME: Unsafe if the user doesn't supply pass or mode
        # TODO: Should probably add a warning here to tell the user that they should use a API key
        api_args["username"] = arguments["username"]
        api_args["password"] = arguments["password"]
        api_args["mode"] = arguments["auth_method"]

    if "api_url" in arguments:
        api_args["base_url"] = arguments["api_url"]

    api_args["user_agent"] = "argus-cli/%s" % __version__

    return ArgusAPI(**api_args)


def main():
    """Used to launch the application"""

    plugin.api = get_api_instance(settings["api"])
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
