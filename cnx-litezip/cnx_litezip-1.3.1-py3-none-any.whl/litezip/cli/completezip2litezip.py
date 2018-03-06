# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import shutil
from pathlib import Path

from litezip import convert_completezip
from litezip.logger import logger
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
        '-o', '--output-dir',
        help="Location to output, rather than converting inplace")
    parser.add_argument(
        'location',
        help="Location of the unpacked completezip")
    return parser


def main(argv=None):
    parser = _arg_parser()
    args = parser.parse_args(argv)

    set_verbosity(args.verbose)

    completezip_path = Path(args.location)
    output_dir = args.output_dir
    if output_dir:
        output_path = Path(output_dir)
        if output_path.exists():
            logger.error("output-dir cannot exist prior to conversion")
            return 1
        shutil.copytree(str(completezip_path), str(output_path))
        completezip_path = output_path

    convert_completezip(completezip_path)

    return 0
