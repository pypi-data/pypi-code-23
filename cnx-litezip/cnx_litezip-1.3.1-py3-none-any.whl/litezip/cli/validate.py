# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

from litezip import parse_litezip, validate_litezip
from .common import set_verbosity


def _arg_parser():
    """Factory for creating the argument parser"""
    description = "Converts a completezip to a litezip"
    parser = argparse.ArgumentParser(description=description)
    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument(
        '-v', '--verbose', action='store_true',
        dest='verbose', default=None,
        help="increase verbosity")
    verbose_group.add_argument(
        '-q', '--quiet', action='store_false',
        dest='verbose', default=None,
        help="print nothing to stdout or stderr")
    parser.add_argument(
        'location',
        help="Location of the unpacked litezip")
    return parser


def main(argv=None):
    parser = _arg_parser()
    args = parser.parse_args(argv)

    set_verbosity(args.verbose)

    struct = parse_litezip(Path(args.location))
    # Logging will provide output based on verbosity.
    errors = validate_litezip(struct)

    return errors and 1 or 0
