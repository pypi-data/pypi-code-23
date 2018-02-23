# -*- coding: utf-8 -*-
'''
dover v0.2.1

dover is a commandline utility for tracking and incrementing project version numbering.

Usage:
  dover [--list] [--debug]
  dover increment (--major|--minor|--patch) [--apply] [--debug]

Options:
  -M --major   Change major dover segment.
  -m --minor   Change minor dover segment.
  -p --patch   Change patch dover segment.
  --debug      Print full exception.
  -h --help    Show this help message
  --version    Show dover app version.

'''
import sys
from docopt import docopt
from . import commands


__author__ = 'Mark Gemmill'
__email__ = 'dev@markgemmill.com'
__version__ = '0.2.1'


def main():
    cargs = docopt(__doc__, version='dover v{}'.format(__version__))

    if cargs['increment']:
        commands.increment(cargs)

    elif cargs['--list']:
        commands.display(cargs)
    else:
        commands.version(cargs)

    sys.exit(0)
