#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Class and methods used to parse command-line arguments.

"""

import logging
import os
import re
import sys
import textwrap
from argparse import HelpFormatter, ArgumentTypeError, Action, ArgumentParser
from datetime import datetime
from gettext import gettext


class MultilineFormatter(HelpFormatter):
    """
    Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __init__(self, prog):
        # Overload the HelpFormatter class.
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _fill_text(self, text, width, indent):
        # Rewrites the _fill_text method to support multiline description.
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text

    def _split_lines(self, text, width):
        # Rewrites the _split_lines method to support multiline helps.
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text


class DirectoryChecker(Action):
    """
    Custom action class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, list):
            checked_vals = [self.directory_checker(x) for x in values]
        else:
            checked_vals = self.directory_checker(values)
        setattr(namespace, self.dest, checked_vals)

    @staticmethod
    def directory_checker(path):
        """
        Checks if the supplied directory exists. The path is normalized without trailing slash.

        :param str path: The path list to check
        :returns: The same path list
        :rtype: *str*
        :raises Error: If one of the directory does not exist

        """
        path = os.path.abspath(os.path.normpath(path))
        if not os.path.isdir(path):
            msg = 'No such directory: {}'.format(path)
            raise ArgumentTypeError(msg)
        return path


def keyval_converter(pair):
    """
    Checks the key value syntax.

    :param str pair: The key/value pair to check
    :returns: The key/value pair
    :rtype: *tuple*
    :raises Error: If invalid pair syntax

    """
    pattern = re.compile(r'([^=]+)=([^=]+)(?:,|$)')
    if not pattern.search(pair):
        msg = 'Bad argument syntax: {}'.format(pair)
        raise ArgumentTypeError(msg)
    key, regex = pattern.search(pair).groups()
    try:
        regex = re.compile(regex)
    except re.error:
        msg = 'Bad regex syntax: {}'.format(regex)
        raise ArgumentTypeError(msg)
    return (key, regex)


class _ArgumentParser(ArgumentParser):
    def error(self, message):
        """
        Overwrite the original method to change exist status.

        """
        self.print_usage(sys.stderr)
        self.exit(99, gettext('%s: error: %s\n') % (self.prog, message))


def init_logging(log, debug=False, level='INFO'):
    """
    Initiates the logging configuration (output, date/message formatting).
    If a directory is submitted the logfile name is unique and formatted as follows:
    ``name-YYYYMMDD-HHMMSS-JOBID.log``If ``None`` the standard output is used.

    :param str log: The logfile directory.
    :param boolean debug: Debug mode.
    :param str level: The log level.

    """
    logname = 'XIOFileChecker-{}-{}'.format(datetime.now().strftime("%Y%m%d-%H%M%S"), os.getpid())
    formatter = logging.Formatter(fmt='%(message)s')
    if log:
        if not os.path.isdir(log):
            os.makedirs(log)
        logfile = os.path.join(log, logname)
    else:
        logfile = os.path.join(os.getcwd(), logname)
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.__dict__[level])
    if log:
        stream_handler = logging.FileHandler(filename='{}.log'.format(logfile), delay=True)
    else:
        stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logging.getLogger().addHandler(stream_handler)
