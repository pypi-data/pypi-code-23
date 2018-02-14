# -*- coding: utf-8 -*-

"""Main module."""

import logging
import logging.config
import yaml
import os.path


def setup(
        conf_file_path="logging.yml",
        default_level=logging.INFO,
        default_format="[%(asctime)s]:%(levelname)s:%(name)s:%(message)s",
        default_datefmt=None,
        default_style=None):

    # Override default values by environment
    arguments = {
        'level': default_level,
        'format': default_format,
        'datefmt': default_datefmt,
        'style': default_style,
    }

    for k in list(arguments.keys()):
        try:
            envionment_text = 'PYTHON_LOGGING_%s' % k.upper()
            if k == 'level':
                arguments[k] = logging._nameToLevel.get(
                    os.environ[envionment_text].strip().upper(),
                    default_level)
            else:
                arguments[k] = os.environ[envionment_text]
        except ValueError:
            pass
        except KeyError:
            pass

    # Remove all arguments that is None value.
    keys = list(arguments.keys())
    for k in keys:
        if arguments[k] is None:
            del arguments[k]

    logging.basicConfig(**arguments)

    # Default configs
    configs = {
        "version": 1,
        # Don't disable existing loggers, so global logger that in other
        # modules will still valid after setup()
        "disable_existing_loggers": False,
        "formatters": {
            "generic": {
                "format": default_format,
            },
        },
        "loggers": {
            "root": {
                "level": logging.getLevelName(arguments["level"]),
                "handlers": ["console"],
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "generic",
            },
        },
    }

    if os.path.exists(conf_file_path):
        configs.update(yaml.load(open(conf_file_path, 'r')))

    logging.config.dictConfig(configs)
