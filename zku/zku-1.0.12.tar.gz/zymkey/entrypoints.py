from __future__ import absolute_import

import importlib
import sys

from cmdline import SettingsParser, settings, setup_logging

setup_logging()


def main():
    SettingsParser.compile_settings()

    subcommand = settings._SUBCOMMAND

    x = importlib.import_module('zymkey.commands.{}'.format(subcommand))

    sys.exit(x.main())
