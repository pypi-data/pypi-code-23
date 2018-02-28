import argparse
from . import decapitator


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

    return parser


def main():
    parser = build_parsers()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
