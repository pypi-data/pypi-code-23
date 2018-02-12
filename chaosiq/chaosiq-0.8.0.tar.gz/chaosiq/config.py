# -*- coding: utf-8 -*-
import os
import os.path

import yaml

from chaosiq.exceptions import ConfigurationMissingError, \
    ConfigurationTokenMissing
from chaosiq.types import Configuration

__all__ = ["initialize_config", "load_config", "CHAOISQ_CONFIG_PATH",
           "DEFAULT_TOKEN", "get_token", "set_token", "set_config_key"]

CHAOISQ_CONFIG_PATH = os.path.abspath(os.path.expanduser("~/.chaosiq/config"))
DEFAULT_TOKEN = "<YOUR TOKEN>"
DEFAULT_CONFIG = {
    "auth": {
        "token": DEFAULT_TOKEN
    }
}


def load_config(config_path: str = CHAOISQ_CONFIG_PATH) -> Configuration:
    """
    Load the chaosiq configuration into memory. Raises
    `ConfigurationMissingError` when the config does not exist.
    """
    if not os.path.exists(config_path):
        raise ConfigurationMissingError(
            "Your chaosiq configuration is missing or is empty. "
            "Run `chaosiq config init` to initialize a default one.")

    with open(config_path) as f:
        return yaml.load(f.read())


def save_config(config: Configuration, config_path: str = CHAOISQ_CONFIG_PATH):
    """
    Save the config on to disk.
    """
    with open(config_path, 'w') as f:
        return f.write(yaml.dump(config, default_flow_style=False))


def initialize_config(config_path: str = CHAOISQ_CONFIG_PATH,
                      force: bool = False):
    """
    Initialize a default configuration on disk. If the cconfiguration already
    exists, it is left untouched, unless the `force` parameter is set to
    `True`.

    The configuration is set to be read and written only by the current user.
    """
    if os.path.exists(config_path) and not force:
        return

    try:
        os.mkdir(os.path.dirname(config_path))
    except FileExistsError:
        pass

    with open(config_path, "w") as f:
        os.chmod(config_path, 0o600)
        f.write(yaml.dump(DEFAULT_CONFIG, default_flow_style=False))


def set_token(email: str, token: str, config: Configuration,
              force: bool = False):
    """
    Save token to the configuration file.
    """
    config["auth"]["email"] = email
    config["auth"]["token"] = token


def get_token(config: Configuration) -> str:
    """
    Get the chaosiq access token from the config and raises errors when it
    is missing or unset.
    """
    token = config.get("auth", {}).get("token")
    if not token:
        raise ConfigurationTokenMissing(
            "Missing chaosiq token, please ensure you "
            "set it in your chaosiq configuration with `chaosiq login`.")

    if token == DEFAULT_TOKEN:
        raise ConfigurationTokenMissing(
            "It seems you have not set your chaosiq token "
            "in the configuration. Please, run `chaosiq login`.")

    return token


def set_config_key(config: Configuration, key: str, value: str):
    """
    Set a value to a key in the configuration. The key may be dotted to
    represent a nested key, the value is set to the last segment of the key.
    """
    tree = {}
    keys = key.split(".")

    c = config
    for k in keys[:-1]:
        if k not in c:
            c[k] = {}
        c = c[k]

    c[keys[-1]] = value
