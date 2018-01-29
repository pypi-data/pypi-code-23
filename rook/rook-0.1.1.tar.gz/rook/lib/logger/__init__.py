if "rook" in __name__:
    # This is caused by not changing sys.path in Rook combined with the way we package the code
    from rook.interfaces.config import LoggingConfiguration
else:
    from interfaces.config import LoggingConfiguration

from .logger_factory import LoggerFactory

def _build_logger():
    import sys
    if "unittest" in sys.argv[0]:
        log_level = 10
        log_to_stderr = True
    else:
        log_level = LoggingConfiguration.LOG_LEVEL
        log_to_stderr = LoggingConfiguration.LOG_TO_STDERR

    return LoggerFactory(
        LoggingConfiguration.LOGGER_NAME,
        log_level,
        LoggingConfiguration.FILE_NAME,
        log_to_stderr,
        LoggingConfiguration.LOG_TO_REMOTE,
        LoggingConfiguration.PROPAGATE_LOGS
    ).get_logger()

logger = _build_logger()
logger.info("Initialized logger")
