# -*- coding: utf-8 -*-
'''
dover v0.1.0

dover is a commandline utility for tracking and incrementing project version numbering.

Usage:
  dover [--format=FORMAT] [--list]
  dover increment (--major|--minor|--patch) [--apply]

Options:
  -M --major   Change major dover segment.
  -m --minor   Change minor dover segment.
  -p --patch   Change patch dover segment.
  -h --help    Show this help message
  --version    Show dover app version.

'''
from . import commands
from docopt import docopt


__author__ = 'Mark Gemmill'
__email__ = 'dev@markgemmill.com'
__version__ = '0.1.0'


def main():
    args = docopt(__doc__, version='dover v{}'.format(__version__))

    if args['increment']:
        commands.increment(cli_args=args)

    elif args['--list']:
        commands.display()

    else:
        commands.version()


if __name__ == "__main__":
    main()
