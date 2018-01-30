#!/usr/bin/python3

import time
import datetime
import os
import sys
import json
from logbook import Logger, StreamHandler


CRITICAL = "CRITICAL"
ERROR = "ERROR"
WARNING = "WARNING"
NOTICE = "NOTICE"
INFO = "INFO"
DEBUG = "DEBUG"

LOG_LEVELS = {
    CRITICAL: 2,
    ERROR: 3,
    WARNING: 4,
    NOTICE: 5,
    INFO: 6,
    DEBUG: 7
}


class UniLogger:
    __instance = None
    logger = None
    context = {}
    messageLevel = ""

    def __init__(self, stream, level):
        """ Virtually private constructor. """
        if UniLogger.__instance != None:
            raise Exception("Logger is already been instantiated")

        UniLogger.__instance = self
        UniLogger.logger = Logger('uni-logger')

        handler = StreamHandler(stream)
        handler.level_name = level
        handler.formatter = self.json_formatter
        handler.push_application()

    @staticmethod
    def builder():
        """ Static access method. """
        if UniLogger.__instance == None:
            UniLogger()
        UniLogger.context = {}

        return UniLogger.__instance

    def json_formatter(self, record, handler):
        """ Compose final json with standard fields. """
        defaultMessage = {
            "message": record.message,
            "app-id": os.environ.get('APPID'),
            "git-hash": os.environ.get('GITHASH'),
            "time": datetime.datetime.now().time().strftime('%H:%M:%S.%f'),
            "env": os.environ.get('ENV'),
            "level_name": self.messageLevel,
            "level": LOG_LEVELS[self.messageLevel]
        }

        return json.dumps({**defaultMessage, **self.context})

    def addContextField(self, key, value):
        """ Add a context field. """
        self.context.update({key: value})

        return self

    def addContextFields(self, newFields):
        """ Add several fields. """
        self.context.update(newFields)

        return self

    def debug(self, message):
        """ Log a message with level debug. """
        self.messageLevel = DEBUG
        self.logger.debug(message)

    def info(self, message):
        """ Log a message with level info. """
        self.messageLevel = INFO
        self.logger.info(message)

    def notice(self, message):
        """ Log a message with level notice. """
        self.messageLevel = NOTICE
        self.logger.notice(message)

    def warning(self, message):
        """ Log a message with level warning. """
        self.messageLevel = WARNING
        self.logger.warning(message)

    def error(self, message):
        """ Log a message with level error. """
        self.messageLevel = ERROR
        self.logger.error(message)

    def critical(self, message):
        """ Log a message with level critical. """
        self.messageLevel = CRITICAL
        self.logger.critical(message)
