"""Exception classes."""


class AMaaSException(Exception):
    """Base class for all AMaaS Exceptions."""


class TransactionNeedsSaving(AMaaSException):
    def __init__(self):
        message = "Transaction needs to be saved to AMaaS Core for the functionality to be valid"
        super(TransactionNeedsSaving, self).__init__(message)


class ConfigurationError(AMaaSException):
    """Configuration error."""


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing."""

    def __init__(self, section, name):
        msg = 'Configuration missing: {section}->{name}'
        super(ConfigurationError, self).__init__(msg.format(section=section, name=name))
