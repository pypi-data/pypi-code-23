"""Menhir command line script.

The script is the main user interface for menhir.
"""
from __future__ import print_function  # NOQA

import argparse
import logging
import sys

from os import getcwd

from menhir import __version__
from menhir.config import project_config
from menhir.tool_utils import call_tool_chain


log = logging.getLogger(__name__)


def main():
    path = getcwd()

    parser = add_remainder_argument(base_parser())
    args, unknown = parser.parse_known_args()
    remainder = args.remainder

    if args.version:
        print('Menhir %s' % __version__)
        sys.exit(0)

    if unknown or not remainder:
        parser_for_help_message().print_help()
        sys.exit(0 if (unknown == ['-h'] or not unknown) else 1)

    if args.verbose and args.log_level != 'DEBUG':
        args.log_level = 'INFO'
    logging.basicConfig(level=args.log_level)
    logging.getLogger('botocore').setLevel('INFO')
    logging.getLogger('boto3').setLevel('INFO')

    write_version()

    info = project_config(args.config_file, dir=path)
    info['menhir'] = {'root': path}

    log.debug('script remainder: %s', remainder)
    result = call_tool_chain(path, info, remainder)
    if result['status'] == 'fail':
        sys.exit(1)

    if result['status'] == 'nothing_to_do' and args.on_no_op == 'fail':
        sys.exit(1)


def add_remainder_argument(parser):
    parser.add_argument('remainder', nargs=argparse.REMAINDER)
    return parser


def add_help_argument(parser):
    parser.add_argument(
        '-h', '--help', help='Print help message and exit.',
        default=False, action='store_const', const=True,
    )
    return parser


def parser_for_help_message():
    parser = base_parser()
    parser = add_help_argument(parser)
    parser = add_generic_tool_parser(parser)
    return parser


def base_parser(**kwargs):
    import argparse
    parser = argparse.ArgumentParser(
        description="""
Menhir is an extensible build tool, that recognises dependencies
between sub-projects in a repository.
    """,
        add_help=False,
        **kwargs
    )
    parser.add_argument(
        "--version",
        default=False,
        action='store_const',
        const=True,
        help="Print menhir version and exit.",
    )
    parser.add_argument(
        "-v", "--verbose",
        default=False,
        action='store_const', const=True,
        help='Provide verbose output (shortcut for log-levl INFO).',
    )
    parser.add_argument(
        "--log-level", default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the log level for program output messages."
    )
    parser.add_argument(
        "--config-file", default='menhir-config.yaml',
        help="File to read configuration from."
    )
    parser.add_argument(
        "--on-no-op",
        default="fail",
        choices=['fail', 'succeed'],
        help='Specify the behaviour if the tool is not applicable.',
    )
    return parser


def add_tool_parser(parser, tool):
    parsers = parser.add_subparsers(dest='tool')
    p = parsers.add_parser(tool.name())
    tool.configure_parser(p)
    return parser


def add_generic_tool_parser(parser):
    parser.add_argument(
        "tool",
        nargs=1,
        help='Tool to invoke.',
    )

    parser.add_argument(
        "arg",
        nargs="*",
        help='Tool arguments',
    )
    return parser


def write_version():
    from menhir import __version__
    with open('.menhir-version', 'w+') as f:
        f.write(__version__)
