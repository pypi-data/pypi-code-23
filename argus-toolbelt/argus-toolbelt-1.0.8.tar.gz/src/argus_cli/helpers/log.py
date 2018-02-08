import logging
from argus_cli.settings import settings

# Set up custom log levels for plugins
PLUGIN_LOG_LEVEL_NUM = 9 
logging.addLevelName(PLUGIN_LOG_LEVEL_NUM, "PLUGIN")

# Set up logging with colored output
logging.config.dictConfig(settings["logging"])


def plugin(self, message, *args, **kws):
    """
    Custom log level for plugins
    """
    self.isEnabledFor(logging.INFO) and self._log(PLUGIN_LOG_LEVEL_NUM, message, args, **kws) 

logging.Logger.plugin = plugin
# Package wide logger
log = logging.getLogger("argus_cli")
log.propagate = False
