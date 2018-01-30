#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from argparse import RawTextHelpFormatter
from rst2ansi import rst2ansi


class RSTHelpFormatter(RawTextHelpFormatter):
    def format_help(self):
        ret = rst2ansi(
            super(RSTHelpFormatter, self).format_help().encode("utf-8") +
            "\n".encode("utf-8"))
        return ret.encode(sys.stdout.encoding,
                          'replace').decode(sys.stdout.encoding)

    def format_usage(self):
        ret = rst2ansi(
            super(RSTHelpFormatter, self).format_usage().encode("utf-8") +
            "\n".encode("utf-8"))
        return ret.encode(sys.stdout.encoding,
                          'replace').decode(sys.stdout.encoding)
