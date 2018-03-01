#!/usr/bin/env python
# coding: utf-8

from dotenv import load_dotenv
from os import environ
import logging
import logging.handlers
import sys


def file_logger(log, envfile):
    load_dotenv(envfile)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(environ.get("LOG_FORMAT"))

    # create file handler which logs even debug messages
    fh = logging.handlers.TimedRotatingFileHandler('/var/log/app.log', when='D', interval=1)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)


def stream_logger(log, envfile):
    load_dotenv(envfile)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(environ.get("LOG_FORMAT"))

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)


class logger:
    def __init__(self, envfile='.env'):
        self.log = None
        self.envfile = envfile

    def __enter__(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)

        stream_logger(self.log, self.envfile)
        file_logger(self.log, self.envfile)

        return self.log

    def __exit__(self, type, value, traceback):
        for handler in self.log.handlers:
            handler.close()
            self.log.removeFilter(handler)
