# -*- coding: utf-8 -*-
from configparser import ConfigParser

DEFAULT_SECTION_HEADER = "DEFAULT"


class _GeneralConfigParser(object):
    config_file = None
    parser = None

    def __init__(self, config_file_path):
        self.parser = ConfigParser()
        self.parser.read_file(_DefaultSectionHeaderConfigFile(config_file_path))

    def get_options(self):
        options = dict(self.parser.items(DEFAULT_SECTION_HEADER))
        for k, v in options.items():
            options[k] = str(v)
        return options


class _DefaultSectionHeaderConfigFile(object):
    config_file = None
    _first_read = True

    def __init__(self, config_file_path):
        self.config_file = open(config_file_path, "r")

    def readline(self):
        if self._first_read:
            self._first_read = False
            return "[%s]" % DEFAULT_SECTION_HEADER
        else:
            return self.config_file.readline()

    def __iter__(self):
        line = self.readline()
        while line:
            yield line
            line = self.readline()
