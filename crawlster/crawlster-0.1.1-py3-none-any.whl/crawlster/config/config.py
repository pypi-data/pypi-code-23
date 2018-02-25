import json
import os

from crawlster.config.options import ListOption, NumberOption
from crawlster.exceptions import OptionNotDefinedError, \
    MissingValueError

#: The core options used by the framework
from crawlster.validators import ValidationError

CORE_OPTIONS = {
    'core.start_urls': ListOption(required=True),
    'core.workers': NumberOption(default=os.cpu_count())
}


class Configuration(object):
    """Configuration object that stores key-value pairs of options"""

    def __init__(self, options=None):
        """Initializes the defined options and the provided values"""
        self.defined_opts = CORE_OPTIONS
        self.values = options or {}

    def register_options(self, options):
        """Registers a mapping of option definitions to the current config"""
        self.defined_opts.update(options)

    def get(self, key):
        """Retrieves a value from this configuration, if available

        Raises:
            OptionNotDefinedError:
                When the option key is not defined by any helper
            MissingValueError:
                When the option key is defined but its value could not be
                determined
            ValidationError:
                When the provided value fails validation
        """
        if key not in self.defined_opts:
            raise OptionNotDefinedError(
                'Option "{}" is not defined'.format(key))
        opt_specs = self.defined_opts[key]
        if key not in self:
            if opt_specs.required:
                raise MissingValueError(
                    'Option {} is required but its value '
                    'could not be determined'.format(key))
            else:
                return opt_specs.get_default_value()
        value = self[key]
        opt_specs.validate(value)
        return value

    def __contains__(self, item):
        """Returns whether the value is explicitly provided by the config"""
        return item in self.values

    def __getitem__(self, item):
        """Directly retrieves the value.

        Raises KeyError if the value is not provided
        """
        return self.values[item]

    def validate_options(self):
        """Validates all the options"""
        for key in self.defined_opts:
            try:
                self.get(key)
            except ValidationError:
                raise
            except (MissingValueError, OptionNotDefinedError):
                # ignore options that are not defined or provided. This
                # method is only supposed to fail if any validator fails
                pass


class JsonConfiguration(Configuration):
    """Reads the configuration from a json file"""

    def __init__(self, file_path):
        """Loads the values from a json file"""
        super(JsonConfiguration, self).__init__()
        with open(file_path, 'r') as fp:
            options = json.load(fp)
        self.values = options
