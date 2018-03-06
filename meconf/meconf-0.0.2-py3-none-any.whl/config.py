import importlib
import os
import re

from .exceptions import ConfigError


# pylint: disable=too-few-public-methods
class NoValue(object):
    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)


class Env:
    NOTSET = NoValue()
    BOOLEAN_TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')

    def __init__(self, env_file=None):
        if env_file:
            parse_env_file(env_file)

    def __call__(self, var, cast=None, default=NOTSET, parse_default=False):
        return self.get_value(var, cast=cast, default=default, parse_default=parse_default)

    def get_value(self, var, cast=None, default=NOTSET, parse_default=False):
        """Return value for given environment variable.

        :param var: Name of variable.
        :param cast: Type to cast return value as.
        :param default: If var not present in environ, return this instead.
        :param parse_default: force to parse default..

        :returns: Value from environment or default (if set)
        """
        try:
            value = os.environ[var]
        except KeyError:
            if default is self.NOTSET:
                error_msg = "Set the {0} environment variable".format(var)
                raise ConfigError(error_msg)

            value = default

        # Resolve any proxied values
        if hasattr(value, 'startswith') and value.startswith('$'):
            value = value.lstrip('$')
            value = self.get_value(value, cast=cast, default=default)

        if value != default or (parse_default and value):
            value = self.parse_value(value, cast)

        return value

    # pylint: disable=too-many-branches
    @classmethod
    def parse_value(cls, value, cast):
        """Parse and cast provided value

        :param value: Stringed value.
        :param cast: Type to cast return value as.

        :returns: Casted value
        """
        if cast is None:
            return value
        elif cast is bool:
            try:
                value = int(value) != 0
            except ValueError:
                value = value.lower() in cls.BOOLEAN_TRUE_STRINGS
        elif isinstance(cast, list):
            value = list(map(cast[0], [x for x in value.split(',') if x]))
        elif isinstance(cast, tuple):
            val = value.strip('(').strip(')').split(',')
            value = tuple(map(cast[0], [x for x in val if x]))
        elif isinstance(cast, dict):
            key_cast = cast.get('key', str)
            value_cast = cast.get('value', str)
            value_cast_by_key = cast.get('cast', dict())
            value = dict(map(
                lambda kv: (
                    key_cast(kv[0]),
                    cls.parse_value(kv[1], value_cast_by_key.get(kv[0], value_cast))
                ),
                [val.split('=') for val in value.split(';') if val]
            ))
        elif cast is dict:
            value = dict([val.split('=') for val in value.split(',') if val])
        elif cast is list:
            value = [x for x in value.split(',') if x]
        elif cast is tuple:
            val = value.strip('(').strip(')').split(',')
            value = tuple([x for x in val if x])
        elif cast is float:
            # clean string
            float_str = re.sub(r'[^\d,\.]', '', value)
            # split for avoid thousand separator and different locale comma/dot symbol
            parts = re.split(r'[,\.]', float_str)
            if len(parts) == 1:
                float_str = parts[0]
            else:
                float_str = "{0}.{1}".format(''.join(parts[0:-1]), parts[-1])
            value = float(float_str)
        else:
            value = cast(value)
        return value


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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=Singleton):
    def __init__(self):
        settings_module_name = os.environ.get('SETTINGS_MODULE')

        if not settings_module_name:
            raise ConfigError('Please set the SETTINGS_MODULE environment variable.')

        settings_module = importlib.import_module(settings_module_name)

        for var in dir(settings_module):
            if not var.isupper():
                continue

            config_value = getattr(settings_module, var)
            setattr(self, var, config_value)


# pylint: disable=invalid-name
config = AppConfig()
