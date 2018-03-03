# -*- coding: utf-8 -*-
'''
dover v0.3.1

dover is a commandline utility for 
tracking and incrementing your 
project version numbers.

Usage:
  dover [--list] [--debug]
  dover increment ((--major|--minor|--patch) [--alpha|--beta|--rc] |
                   [--major|--minor|--patch] (--alpha|--beta|--rc)) 
                   [--apply] [--debug] [--no-list]

Options:
  -M --major     Update major version segment.
  -m --minor     Update minor version segment.
  -p --patch     Update patch version segment.
  -a --alpha     Update alpha pre-release segment.
  -b --beta      Update beta pre-release segment.
  -r --rc        Update release candidate segment.
  -x --no-list   Do not list files.
  --debug        Print full exception info.
  -h --help      Display this help message
  --version      Display dover version.

'''
import sys
from docopt import docopt
from . import commands


__author__ = 'Mark Gemmill'
__email__ = 'dev@markgemmill.com'
__version__ = '0.3.1'


def main():
    cargs = docopt(__doc__, version='dover v{}'.format(__version__))

    if cargs['increment']:
        commands.increment(cargs)

    elif cargs['--list']:
        commands.display(cargs)
    else:
        commands.version(cargs)
