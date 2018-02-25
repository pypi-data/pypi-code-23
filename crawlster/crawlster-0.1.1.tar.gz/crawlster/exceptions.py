class CrawlsterError(Exception):
    """Base exception for application specific exceptions"""
    pass


class ConfigurationError(CrawlsterError):
    """Thrown when configuration is invalid"""


class OptionNotDefinedError(CrawlsterError):
    """Thrown when trying to access an option that is not defined"""


class MissingValueError(CrawlsterError):
    """Thrown when a required config value is not provided"""


missing_config_msg = """The configuration is not properly initialized.
It seems you forgot to declare the config attribute for the crawler?
"""


def get_full_error_msg(msg_id):
    return ERROR_MSGS[msg_id]


ERROR_MSGS = {
    'missing_config': missing_config_msg
}
