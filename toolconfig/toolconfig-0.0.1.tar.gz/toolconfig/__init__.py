import json
import os


def _expand(config, path_vars):
    if path_vars:
        for key in config:
            if key not in path_vars:
                continue

            config[key] = os.path.expanduser(config[key])
    return config


def read(config_name, path='~/.config', section="default",
         path_vars=None):
    fullpath = "%s/%s.conf" % (os.path.expanduser(path), config_name)

    with open(fullpath) as config_file:
        config = json.load(config_file)

        if section:
            config = _expand(config[section], path_vars)
        else:
            for config_section in config:
                config[config_section] = _expand(config[config_section],
                                                 path_vars)

        return config
