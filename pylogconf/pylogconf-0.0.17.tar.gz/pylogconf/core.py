import os
import os.path
import logging.config
import logging
import sys

# noinspection PyPackageRequirements
import traceback

import yaml
import logging_tree
from pyfakeuse.pyfakeuse import fake_use


def is_2():
    return sys.version_info[0] == 2


# noinspection PyPackageRequirements,PyUnresolvedReferences
def setup_scrapy():
    """ This is not needed as we pass 'LOG_ENABLED':False to scrapy at init time """

    def replace_configure_logging(install_root_handler=False, settings=None):
        fake_use(install_root_handler)
        fake_use(settings)

    def replace_log_scrapy_info(settings=None):
        fake_use(settings)

    # scrapy stuff
    import scrapy.utils.log  # for configure_logging
    import scrapy.crawler  # configure_logging, log_scrapy_info
    logging_settings = {
        'LOG_ENABLED': False,
        'LOG_LEVEL': logging.WARN,
    }
    scrapy.utils.log.configure_logging(install_root_handler=False, settings=logging_settings)
    # are you watching closely?!?
    scrapy.crawler.configure_logging = replace_configure_logging
    scrapy.crawler.log_scrapy_info = replace_log_scrapy_info
    # print(scrapy.utils.log.log_scrapy_info)


# these control how to exception hook works
# these are also their default values (unless overridden by environment variables)
_print_traceback = False
_drill = True


def _excepthook(etype, value, tb):
    logger = logging.getLogger(__name__)
    # print the traceback but only if configured to do so
    if _print_traceback:
        traceback.print_exception(
            etype=etype,
            value=value,
            tb=tb,
        )
    # this loop will drill to the core of the problem
    # use only if this is what you want to show...
    # note that exception chaining is only a python 3 feature.
    if _drill and not is_2():
        while value.__cause__:
            value = value.__cause__
    logger.error("Exception occurred, type [%s], value [%s]" % (etype, value))


def _str2bool(s):
    """ convert a string to a boolean value """
    return s in {"True", "T", "true", "t", "yes", "y", "1"}


def setup_exceptions():
    """ Only print the heart of the exception and not the stack trace """
    # first set up the variables needed by the _excepthook function
    global _print_traceback, _drill
    local_print_traceback = os.getenv("PYLOGCONF_PRINT_TRACEBACK")
    if local_print_traceback is not None:
        _print_traceback = _str2bool(local_print_traceback)
    local_drill = os.getenv("PYLOGCONF_DRILL")
    if local_drill is not None:
        _drill = _str2bool(local_drill)
    # now that everything is ready attach the hook
    sys.excepthook = _excepthook


def setup_logging():
    """ setup the logging system """
    default_path_yaml = os.path.expanduser('~/.pylogconf.yaml')
    default_path_conf = os.path.expanduser('~/.pylogconf.conf')
    # this matches the default logging level of the logging
    # library and makes sense...
    default_level = logging.WARNING

    dbg = os.getenv("PYLOGCONF_DEBUG", False)

    """ try YAML config file first """
    value = os.getenv('PYLOGCONF_YAML', None)
    if value is None:
        path = default_path_yaml
    else:
        path = value
    if os.path.isfile(path):
        _debug('found logging configuration file [{0}]...'.format(path), dbg)
        with open(path) as f:
            config = yaml.load(f.read())
            logging.config.dictConfig(config)
            return

    """ Now try regular config file """
    value = os.getenv('PYLOGCONF_CONF', None)
    if value is None:
        path = default_path_conf
    else:
        path = value
    if os.path.isfile(path):
        _debug('found logging configuration file [{0}]...'.format(path), dbg)
        logging.config.fileConfig(path)
        return

    _debug('logging with level [{0}]...'.format(default_level), dbg)
    logging.basicConfig(level=default_level)


def setup():
    """
    This is the main API that this module exposes. It sets up logging and exception handling
    :return:
    """
    setup_logging()
    setup_exceptions()


def show_tree():
    """ Show the logging tree """
    logging_tree.printout()


def _debug(msg, dbg):
    """
    debugging method for this module. Why do we need this? Why not use logging? Because we are setting up logging!
    The regular chicken and egg problem...
    :param msg:
    :param dbg:
    :return:
    """
    if dbg:
        print(msg)
