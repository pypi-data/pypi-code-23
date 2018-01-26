#
# Copyright (c) 2016 BlueData Software, Inc.
#
import logging

class Wblog(object):
    """

    """
    LOG = None
    LOG_CMD = None
    LOG_FILE = None

    def __init__(self, config):
        logDir = config.get(SECTION_WB, KEY_LOGDIR)

        if self.LOG == None:
            LOG = logging.getLogger('bdwb')

            console_format = logging.Formatter('%(message)s')
            console_hdlr = logging.StreamHandler()
            console_hdlr.setLevel(logging.INFO)
            console_hdlr.setFormatter(console_format)
            LOG.addHandler(console_hdlr)

        if self.LOG_FILE == None:
            LOG_FILE = logging.getLogger('bdwb.file')
            file_formatter = logging.Formatter('%(asctime)s %(module)s %(lineno)d %(levelname)s : %(message)s')
            file_hdlr = logging.handlers.FileHandler()
            file_hdlr.setLevel(logging.DEBUG)
            file_hdlr.setFormatter(file_formatter)
            LOG_FILE.addHandler(file_hdlr)

        if self.LOG_CMD == None:
            LOG_CMD = logging.getLogger('bdwb.cmd')

            file_formatter = logging.Formatter('%(message)s')
            file_hdlr = logging.handlers.FileHandler(config.getCmdLogFileName())
            file_hdlr.setLevel(logging.INFO)
            file_hdlr.setFormatter(file_formatter)
            LOG_CMD.addHandler(file_hdlr)

    def debug(self, *args, **kwargs):
        self.LOG.debug(args, kwargs)

    def info(self, *args, **kwargs):
        self.LOG.info(args, kwargs)

    def warn(self, *args, **kwargs):
        self.LOG.warning(args, kwargs)

    def error(self, *args, **kwargs):
        self.LOG.error(args, kwargs)

    def instruction(self, *args, **kwargs):
        self.LOG_CMD.info(args, kwargs)

__all__ = ['Wblog']
