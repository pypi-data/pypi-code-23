"""
Module that loads the configuration details from a YAML file.
"""
from yaml import load, safe_dump
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from dict_recursive_update import recursive_update as _update
import munch
import pathlib

_configuration_file_location = pathlib.Path('/')

# This is the default settings object. It is in dictionary form, but will be accessed using object notation once the
# configuration file has been loaded.
#
# i.e. processing['output'] will be processing.output instead.
_settings = {
    'processing': {
        # List of log directories that should be processed in order to find content
        'inputs': ['log'],
    },
    'site': {
        # This is the default title of the site
        'title': 'Development Log',

        # This is the timezone that the site will be generated using
        'timezone': 'UTC',
    }
}


def get_configuration_root():
    """Provides the location of the configuration file's containing directory."""
    return _configuration_file_location.parent


def add_default_configuration(key, configuration):
    """
    Method call that will add default settings, should only be called before initialize event is fired off
    :param key: key to namespace the configuration settings away
    :param configuration:
    """
    _settings[key] = configuration


def load_configuration_file(file_name):
    """
    Load the requested configuration file into memory so that the rest of the application can be configured.
    :param file_name: filename to open and load settings from
    :return: object containing settings.
    """
    global _settings, _configuration_file_location

    _configuration_file_location = pathlib.Path(file_name).resolve()

    try:
        with open(file_name, 'r') as configuration_file:
            _loaded_configuration = load(configuration_file, Loader=Loader)
            if _loaded_configuration:
                _update(_settings, _loaded_configuration)
    except FileNotFoundError:
        pass

    return munch.Munch.fromDict(_settings)


def get_configuration():
    """Returns objects with unmodified settings."""
    return munch.Munch.fromDict(_settings)


def dump_configuration(configuration_file, configuration=None):
    """
    Dump the configuration object to the provided file.
    :param configuration_file:
    :param configuration: overridden configuration file to save off.
    :return:
    """
    if configuration is None:
        configuration = get_configuration()

    with open(configuration_file, 'w') as configuration_file:
        safe_dump(configuration.toDict(), configuration_file, default_flow_style=False)
