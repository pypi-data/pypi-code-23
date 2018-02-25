from crawlster.validators import validate_isinstance, one_of, is_url


class ConfigOption(object):
    """Class for configuration option definitions"""

    def __init__(self, validators, default=None, required=False):
        """Initializes the config option

        If required is True, the user must provide the option in his Crawlster
        concrete implementation, otherwise will raise
        :py:class:`MissingValueError`

        Args:
            validators (list of callable):
                A list of validator callables.
            default:
                The default value to be returned if the user does not
                explicitly provides it. Is ignored if required is True.
                If a callable is provided, the default value is determined
                as the result of it being called with no arguments.
            required (bool):
                Specifies if the user must provide the value in the crawler
                class definition
        """
        self.validators = validators
        self.default = default
        self.required = required

    def get_default_value(self):
        """Determines the default value"""
        if callable(self.default):
            return self.default()
        else:
            return self.default

    def validate(self, value):
        """Runs all validators against a provided value

        Raises:
            ValidationError:
                When the validation fails

        Returns:
            None when validation succeeds
        """
        for validator in self.validators:
            validator(value)


#: alias for the config option as being an optional value
Optional = ConfigOption


class Required(ConfigOption):
    """A required value that the user must provide."""

    def __init__(self, validators):
        """Initializes the config option with the determined validators"""
        super(Required, self).__init__(validators, required=True)


class OptionWithDefaultValidators(ConfigOption):
    """Base class for options that have default validators"""
    default_validators = []

    def __init__(self, default=None, required=False, extra_validators=None):
        """Initializes the config options.

        Args:
            default:
                Same as :py:class:`ConfigOption`
            required:
                Same as :py:class:`ConfigOption`
            extra_validators:
                A list of extra validators to be used with the default ones
        """
        validators = self.default_validators + (extra_validators or [])
        super(OptionWithDefaultValidators, self).__init__(validators,
                                                          default,
                                                          required)


class NumberOption(OptionWithDefaultValidators):
    """A numeric option"""
    default_validators = [validate_isinstance((int, float))]


class StringOption(OptionWithDefaultValidators):
    """A string option"""
    default_validators = [validate_isinstance(str)]


class ListOption(OptionWithDefaultValidators):
    """A list/tuple option"""
    default_validators = [validate_isinstance((list, tuple))]


class ChoiceOption(ConfigOption):
    """An option whose value must be one from the specified choices"""

    def __init__(self, choices, default=None, required=False,
                 extra_validators=None):
        if default not in choices:
            msg = 'The default value is not in the specified choices'
            raise ValueError(msg)
        validators = [one_of(choices)] + (extra_validators or [])
        super(ChoiceOption, self).__init__(validators, default, required)


class UrlOption(OptionWithDefaultValidators):
    """An option whose value must be a valid URL"""
    default_validators = [is_url]
