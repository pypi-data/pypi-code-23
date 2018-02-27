import os
import re

from .exceptions import ConfigError


# pylint: disable=too-few-public-methods
class Config:
    def __init__(self):
        self._config = {}

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            raise ConfigError('Config parameter "{}" is not defined.'.format(item))


# pylint: disable=invalid-name
config = Config()


# pylint: disable=too-few-public-methods
class NoValue(object):
    """
    Dummy class for when a config value has no default.
    """
    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)


def env(env_name, default=NoValue(), cast=str):
    """
    Create config variables settings.

    :param env_name: The name of the environment variable.
    :param default: The default value that should be assigned.
    :param cast: Cast the value to given type.
    :return: Variable settings.
    """
    return {
        'name': env_name,
        'default': default,
        'cast': cast,
    }


def get_from_env(name, default, cast):
    """
    Get an environment variable according to the passed settings. This can be any dict that
    conforms the required fields, but for convenience is is recommended to use the output
    from `env()`.

    :param name: The name of the environment variable.
    :param default: The default value that should be assigned.
    :param cast: Cast the value to given type.
    :return: The desired config value.
    :raise: ConfigError
    """

    config_value = os.environ.get(name, default)

    if isinstance(config_value, NoValue):
        raise ConfigError('Config value {} not set and has no default value.'.format(name))

    return cast(config_value)


def parse_env_file(path):
    """
    Parse and environment file.

    :param path: Path to the environment file.
    """
    if not path.exists():
        raise ConfigError('.env file not found.')

    with open(path) as f:
        for line in f.read().splitlines():
            match = re.match(r'\A(?P<key>[A-Za-z_0-9]+)=(?P<value>.*)\Z', line)
            if match:
                key, val = match.group('key'), match.group('value')

                # remove any " or ' at the beginning or end.
                match2 = re.match(r"\A[\"\']?(?P<value>.*)[\"\']?\Z", val)
                if match2:
                    val = match2.group('value')

                os.environ.setdefault(key, str(val))


def parse_config(app, app_config, env_file=None):
    """
    Parse a given config dict and set the values on the app's settings.

    :param app: Tornado app .
    :param app_config: Config dictionary.
    :param env_file: Optional path to environment file.
    """
    if env_file:
        parse_env_file(env_file)

    for config_name, config_settings in app_config.items():
        value = get_from_env(**config_settings)
        app.settings[config_name] = value

        setattr(config, config_name, value)
