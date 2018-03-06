import os
import collections
import re
import yaml


class ConfigurationEnvironmentError(ValueError):
    pass


class ConfigurationError(ValueError):

    def __init__(self, arg_var, env_var):
        self.message = "Argument '{}' or environment variable '{}' are required.".format(arg_var, env_var)

    def __str__(self):
        return self.message


def load_config_file(file):
    with open(file, 'r') as stream:
        for data in yaml.load_all(stream):
            yield data


def load_config_files(directory, files):
    for name in files:
        file = os.path.join(directory, name)
        if os.path.isfile(file):
            yield from load_config_file(file)
        else:
            pass


def merge(a: dict, b: dict) -> dict:
    if b:
        for k, v in b.items():
            if isinstance(v, collections.Mapping):
                key = a.get(k, {})
                result = merge(key, v)
                a[k] = result
            else:
                a[k] = b[k]
    return a


class Configuration:

    def __init__(self, directory=None, files=None, environment=None, environments=None, exceptions=False, allow_os_override=True):
        """
        Constructs a Configuration object used to read config settings.
        :param directory: The directory where the files are located.
        :param files: A list of files to load.
        :param environment: The environment to use. Defaults to 'development'.
        :param environments: A list of environments to support.
        :param exceptions: If True, raises a KeyError when a setting is not found, otherwise returns None.
        :param allow_os_override: If True, allows OS environment variables to override a setting value.
        """

        # the directory we will load from
        self.directory = directory or os.environ.get('CONFIG_DIR')
        if not self.directory:
            raise ConfigurationError('directory', 'CONFIG_DIR')

        # the files we will load
        if not files:
            files = os.environ.get('CONFIG_FILES')
            files = files.split(' ') if files else None

        if not files:
            files = ['config.yml', 'localhost.yml', 'secrets.yml']

        self.files = files

        # the environments we will support
        if not environments:
            environments = os.environ.get('CONFIG_ENVS')
            environments = environments.split(' ') if environments else None

        if not environments:
            environments = ['production', 'staging', 'development', 'testing']

        self.environments = environments

        # the current environment
        self.environment = environment or os.environ.get('CONFIG_ENV') or 'development'
        if not self.environment:
            raise ConfigurationError('environment', 'CONFIG_ENV')

        # make sure environment is one of the items in environments
        if self.environment not in self.environments:
            raise ConfigurationEnvironmentError("The environment '{}' is not in environments list: {}".format(self.environment, self.environments))

        # default exception raise configuration
        self.exceptions = exceptions

        # allow os environment variables to fill in settings with no value
        self.allow_os_override = allow_os_override

        # the dicts from the files we load
        self.config_files = []

        # the configs as merged/built
        self.configs = {}

        self.reload()

    def reload(self):
        self.config_files = list(load_config_files(self.directory, self.files))
        self.configs = {}
        baseline = {}

        # load configs for each environment, each environment is the baseline for the next
        for environment in self.environments:
            # build a config for that environment, inheriting from the last baseline config, this becomes the new baseline
            baseline = self._build_config(environment, baseline)

            # save that environment's config
            self.configs[environment] = baseline

    def get(self, path=None, default=None, environment='development', exceptions=None, allow_os_override=None):
        """
        Returns a value from the configuration, given the current environment.
        :param path: The path identifying the setting.
        :param default: A default value to load, if none is found within the config, or OS (if allow_os_override is enabled).
        :param environment: The environment to load from. Default is 'development'.
        :param exceptions: If True and a setting path is not found, a KeyError is raised.
        :param allow_os_override: A flag that allows OS environment variables to override a value.
        :return:
        """

        if exceptions is None:
            exceptions = self.exceptions

        if allow_os_override is None:
            allow_os_override = self.allow_os_override

        config = self.configs[environment]

        last_key = None
        if path:
            keys = re.split('[.:/]', path)
            for key in keys:
                last_key = key
                try:
                    # walk down the key path into the config until the last key is found
                    config = config[int(key)] if key.isdigit() else config[key]
                except KeyError:
                    if exceptions:
                        raise
                    config = None
                    break

        # at this point, config is either none or the value, as we have walked key-by-key into the dict
        value = config

        # fallback on os environment variables
        if allow_os_override and last_key:
            os_value = os.environ.get(last_key)
            if os_value:
                value = os_value

        # value or default
        return value if value is not None else default

    def _build_config(self, environment='development', baseline=None):

        # clone baseline
        config = merge({}, baseline)

        # merge in the environment keys from all discovered config files
        for config_file in self.config_files:
            if environment in config_file:
                merge(config, config_file[environment])

        return config

