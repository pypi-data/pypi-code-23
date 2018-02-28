import argparse
from . import decapitator
from . import squares
from . import rot13
from . import cubify


def build_parsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command_name")
    subparsers.required = True

    parser.add_argument('--version', help="output m3m3s' version and halt.",
                        action='version',
                        version=f"m3m3s {__version__}")

    parser_decap = subparsers.add_parser('decap')
    decapitator.add_args_to_parser(parser_decap)
    parser_decap.set_defaults(func=decapitator.main)

    parser_squares = subparsers.add_parser('squares')
    squares.add_args_to_parser(parser_squares)
    parser_squares.set_defaults(func=squares.main)

    parser_rot13 = subparsers.add_parser('rot13')
    rot13.add_args_to_parser(parser_rot13)
    parser_rot13.set_defaults(func=rot13.main)

    parser_cubify = subparsers.add_parser('cubify')
    cubify.add_args_to_parser(parser_cubify)
    parser_cubify.set_defaults(func=cubify.main)

    return parser


def main():
    parser = build_parsers()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
