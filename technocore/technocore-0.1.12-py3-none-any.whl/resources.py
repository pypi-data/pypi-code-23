#!/usr/bin/env python3
import os
import sys
import logging
import platform

""" The resource module.

This module creats a consistent way for the application to get the path to
resourses, e.g. images. All application resourses most have unike names, e.g.
"icon.png"

This module provide an application logger. This module provide global names on
application files. """

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["get_application_path", "get_resource_path", "logg_system_info",
        "logger"]


def get_application_path(name):
    """Return the OS spesific system path for the application data."""
    try:
        global logger
        logger.debug("Getting application path for: " + name)
    except Exception:
        # If the application logger is not created yet.
        # The application logger need a path to be stored.
        pass
    if platform.system() == "Darwin":
        path = "~/Applications/" + name + "/"
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    elif platform.system() == "Windows":
        path = "~\\AppData\\" + name + "\\"
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    elif platform.system() == "Linux":
        path = "~/." + name + "/"
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    else:
        logger.debug("Unable to recognize OS, thus no path.")
        raise OSError("Unable to recognize OS, thus no path.")


def get_resource_path(name):
    """Return the full runtime path for a resource."""
    global logger
    logger.debug("Got resource: " + name)
    try:
        # Application is running as a single file
        path = os.path.join(sys._MEIPASS, "./resources/")
    except Exception:
        # Application is run from source code
        path = os.path.dirname(os.path.abspath(__file__)) + "/resources/"
    finally:
        filename = path + name
        return filename


class loggFilter(logging.Filter):
    """A logging filter that filter out level if ignore is True."""
    def __init__(self, level, reject):
        """Constructor:
        * level - The level it applies for (DEBUG, INFO, etc).
        * ignore - If ignore is True, level is ignored."""
        self.level = level
        self.reject = reject

    def filter(self, record):
        """Filter function. Return True if message is passing the filter."""
        if self.reject:
            return (record.levelno != self.level)
        else:
            return (record.levelno == self.level)


def logg_system_info():
    global logger
    logger.debug("Platform: " + str(platform.platform()))
    logger.debug("Operating System: " + str(platform.system()))
    logger.debug("Operating System Relase: " + str(platform.release()))
    logger.debug("Operating System Version: " + str(platform.version()))
    logger.debug("Python version: " + str(sys.version_info))
    # import tkinter
    # logger.debug("tkinter version: " + str(tkinter.TkVersion))


def create_logger(app_name, logger_name, logger_file):
    """Return a logger created from Pythons standard logging library."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s ")
    path = get_application_path(name=app_name)
    filename = path + logger_file

    # Creats a new logfile when the application starts.
    if os.path.isfile(filename):
        os.remove(filename)
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Printing to consol
    stream_handler = logging.StreamHandler()
    debug_filter = loggFilter(logging.DEBUG, False)
    info_filter = loggFilter(logging.INFO, False)
    stream_handler.addFilter(debug_filter)
    stream_handler.addFilter(info_filter)
    logger.addHandler(stream_handler)

    # Logg something
    logger.debug("Application logger created.")
    return logger


APP_NAME = "Journal"
APP_DATABASE = "application.db"
LOGGER_NAME = "application"
LOGGER_FILE = "application.log"
USER_DATABASE = "database.db"
logger = create_logger(app_name=APP_NAME, logger_name=LOGGER_NAME,
                       logger_file=LOGGER_FILE)
logg_system_info()
