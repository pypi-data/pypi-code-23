from .decorators import *
from . import config


def configure(**options):
    for option, value in options.items():
        config_name = option.upper()
        if not hasattr(config, config_name):
            raise ValueError("Option '%s' doesn't exist for reloadable" % config_name)
        setattr(config, config_name, value)
