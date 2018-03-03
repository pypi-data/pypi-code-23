# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging
import logging.handlers
import threading

import os

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.tcell_log_formatter import TCellLogFormatter

_PROCESS_SPECIFIC_LOGGERS = {}
_PROCESS_SPECIFIC_LOGGERS_LOCK = threading.Lock()
_APPFW_PROCESS_SPECIFIC_LOGGERS_LOCK = threading.Lock()
_MAX_BYTES = 10 * 1024 * 1024


def get_level_from_string(level_string):
    if level_string == "DEBUG":
        return logging.DEBUG
    if level_string == "INFO":
        return logging.INFO
    if level_string == "WARNING":
        return logging.WARNING
    if level_string == "ERROR":
        return logging.ERROR
    if level_string == "CRITICAL":
        return logging.CRITICAL


def create_logger_for_process():
    new_logger = logging.getLogger("[{pid}] - tcell".format(pid=os.getpid()))

    logging_options = CONFIGURATION.logging_options
    if logging_options["enabled"]:
        formatter = TCellLogFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s[%(tcell_version)s]: %(message)s')
        new_logger.setLevel(get_level_from_string(logging_options["level"]))

        process_qualified_filename = "{pid}-{name}".format(pid=os.getpid(), name=logging_options["filename"])
        full_path = os.path.join(CONFIGURATION.log_directory, process_qualified_filename)
        file_handle = logging.handlers.RotatingFileHandler(full_path, maxBytes=_MAX_BYTES, backupCount=5)

        file_handle.setFormatter(formatter)
        new_logger.addHandler(file_handle)
    else:
        new_logger.addHandler(logging.NullHandler())

    return new_logger


def get_module_logger(module_name):
    process_id_str = str(os.getpid())
    if process_id_str not in _PROCESS_SPECIFIC_LOGGERS:
        try:
            _PROCESS_SPECIFIC_LOGGERS_LOCK.acquire()
            # now that the lock has been acquired, double check to avoid race conditions
            if process_id_str not in _PROCESS_SPECIFIC_LOGGERS:
                _PROCESS_SPECIFIC_LOGGERS[process_id_str] = create_logger_for_process()
        finally:
            _PROCESS_SPECIFIC_LOGGERS_LOCK.release()

    return _PROCESS_SPECIFIC_LOGGERS[process_id_str].getChild(module_name)


def get_appfw_payloads_logger():
    appfw_logger_key = "{pid}-appfw".format(pid=os.getpid())

    if appfw_logger_key not in _PROCESS_SPECIFIC_LOGGERS:
        try:
            _APPFW_PROCESS_SPECIFIC_LOGGERS_LOCK.acquire()
            # now that the lock has been acquired, double check to avoid race conditions
            if appfw_logger_key not in _PROCESS_SPECIFIC_LOGGERS:
                appfw_logger = logging.getLogger("[{pid}] - appfw-payloads".format(pid=os.getpid()))
                formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s')
                process_qualified_filename = "{pid}-{name}".format(
                    pid=os.getpid(),
                    name=CONFIGURATION.app_firewall_payloads_log_filename)
                full_path = os.path.join(CONFIGURATION.log_directory, process_qualified_filename)
                file_handle = logging.handlers.RotatingFileHandler(full_path, maxBytes=_MAX_BYTES, backupCount=5)
                file_handle.setFormatter(formatter)
                appfw_logger.addHandler(file_handle)

                appfw_logger.setLevel(logging.INFO)

                _PROCESS_SPECIFIC_LOGGERS[appfw_logger_key] = appfw_logger
        finally:
            _APPFW_PROCESS_SPECIFIC_LOGGERS_LOCK.release()

    return _PROCESS_SPECIFIC_LOGGERS[appfw_logger_key]
