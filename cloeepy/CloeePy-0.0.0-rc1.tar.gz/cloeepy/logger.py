import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

from cloeepy.config import Config, obj

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom Log formatter for JSON logs
    """
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        # timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()

        # level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

class Logger(object):
    """
    Logger class that defines logging.Logger instance using default text formatter
    or custom JSON formatter

    Two loggers are created and included as instance attributes of this lass

    logger:
        Used by applications built on CloeePy, and may contain custom fields
        and formatting
    _logger:
        Used internally by CloeePy framework and plugins and uses default
        formatting
    """
    # default json format string
    default_json_fmt = "(timestamp) (level) (message) (filename) (lineno)"
    # default text format string
    default_text_fmt = "timestamp=%(asctime)s level=%(levelname)s message=%(message)s file=%(filename)s line=%(lineno)d"

    def __init__(self, config:object=obj({})):
        self._config = config
        self._set_formatter()
        self._set_log_level()
        self._set_framework_logger()
        self._set_application_logger()

    def _set_formatter(self):
        """
        Inspects config and sets the name of the formatter to either "json" or "text"
        as instance attr. If not present in config, default is "text"
        """
        if hasattr(self._config, "formatter") and self._config.formatter == "json":
            self._formatter = "json"
        else:
            self._formatter = "text"

    def _set_log_level(self):
        """
        Inspects config and sets the log level as instance attr. If not present
        in config, default is "INFO".
        """
        # set log level on logger
        log_level = "INFO"
        if hasattr(self._config, "level") and self._config.level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = self._config.level.upper()
        self._log_level = log_level

    def _set_framework_logger(self):
        """
        Creates a logger with default formatting for internal use by the CloeePy
        framework and its plugins. User may configure customer fields on their
        logger, but the framework would not know how to incorporate those custom
        fields, and by design of the logging pkg authors, the program would error
        out.
        """
        formatter = None
        if self._formatter == "json":
            formatter = CustomJsonFormatter(self.default_json_fmt)
        else:
            formatter = logging.Formatter(self.default_text_fmt)

        self._logger = logging.getLogger("CloeePyFramework")
        logHandler = logging.StreamHandler()
        logHandler.setFormatter(self._formatter)
        self._logger.addHandler(logHandler)
        self._logger.setLevel(self._log_level)

    def _set_application_logger(self):
        """
        Creates a logger intended for use by applications using CloeePy. This logger
        is fully configurable by the user and can include custom fields
        """
        formatter = None
        if self._formatter == "json":
            if hasattr(self._config, "formatString"):
                formatter = CustomJsonFormatter(self._config.formatString)
            else:
                formatter = CustomJsonFormatter(self.default_json_fmt)
        else:
            if hasattr(self._config, "formatString"):
                formatter = logging.Formatter(self._config.formatString)
            else:
                formatter = logging.Formatter(self.default_txt_fmt)

        # get logging.Logger instance and set formatter
        self.logger = logging.getLogger('CloeePyApplication')
        logHandler = logging.StreamHandler()
        logHandler.setFormatter(formatter)
        self.logger.addHandler(logHandler)
        self.logger.setLevel(self._log_level)
