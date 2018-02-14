# -*- coding: utf-8 -*-

"""Main module."""

import logging
import logging.config
import yaml
import os.path
import copy


def merge_dict(dict1, dict2):
    """
    Merge dict1 and dict2 just like update() of dict but if the element is a
    dict we will merge it with the same element inside dict2 and won't replace
    it directly.
    """

    # Overwrite same parts in dict1 from dict2
    for k, v in dict1.items():
        if k not in dict2:
            continue

        if not isinstance(v, dict):
            dict1[k] = dict2[k]
            continue

        merge_dict(dict1[k], dict2[k])

    # Merge missing parts from dict2
    for k, v in dict2.items():
        if (k in dict1) and isinstance(v, dict):
            continue

        dict1[k] = dict2[k]


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
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "generic",
            },
        },
        "loggers": {
            "root": {
                "level": logging.getLevelName(arguments["level"]),
                # Inherit default logger 'handlers' settings
            },
        },

        # Default logger's settings (All loggers will use these settings)
        # They will all use the 'console' handler by default, so you don't
        # have to add 'console' handler to 'handlers' of loggers
        'root': {
            'level': logging.getLevelName(arguments["level"]),
            'handlers': ['console'],
        },

    }

    if os.path.exists(conf_file_path):
        merge_dict(configs, yaml.load(open(conf_file_path, 'r')))

    logging.config.dictConfig(configs)
