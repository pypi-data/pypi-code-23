# -*- coding: utf-8 -*-
from typing import List, Dict
import logging
import sys
import argparse

import trawsate
from trawsate.__init__ import __title__, __description__


logger = logging.getLogger(__name__)


def _parse_args(argv: List[str]) -> argparse.Namespace:
    """
    Interpret command line arguments.

    :param argv: `sys.argv`
    :return: The populated argparse namespace.
    """

    parser = argparse.ArgumentParser(prog=__title__,
                                     description=__description__)
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s ' + trawsate.__version__)
    parser.add_argument('-v', '--verbosity',
                        help='increase output verbosity',
                        action='count',
                        default=0)
    parser.add_argument('-t', '--token',
                        help='a valid Travis API token for interaction with '
                             'the service',
                        required=True)
    parser.add_argument('-p', '--parallelism',
                        help='the maximum number of keys to rotate in '
                             'parallel',
                        type=int,
                        default=20)
    parser.add_argument('username_repo_maps',
                        help='one or more mappings of the form '
                             '"<username>:<repo slug>"',
                        nargs='+')
    return parser.parse_args(argv[1:])


def _log_level_from_vebosity(verbosity: int) -> int:
    """
    Get the `logging` module log level from a verbosity.

    :param verbosity: The number of times the `-v` option was specified.
    :return: The corresponding log level.
    """
    if verbosity == 0:
        return logging.WARNING
    if verbosity == 1:
        return logging.INFO
    return logging.DEBUG


def _maps_to_dict(maps: List[str]) -> Dict[str, str]:
    """
    Turns a list of colon-separated maps into a config dict.

    :param maps: The list of maps.
    :return: The transformed list as a dict.
    """
    usernames_slugs = {}
    for map_ in maps:
        user, repo = map_.split(':', 1)
        usernames_slugs[user] = repo
    return usernames_slugs


def main(argv: List[str]) -> int:
    """
    Trawsate's entry point.

    :param argv: Command line arguments, with the program name in position 0.
    :return: The return code of the program.
    """
    args = _parse_args(argv)

    # sort out logging output and level
    level = _log_level_from_vebosity(args.verbosity)
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    root.addHandler(handler)

    usernames_slugs = _maps_to_dict(args.username_repo_maps)
    logger.debug('Parsed %d maps', len(usernames_slugs))
    rotator = trawsate.Rotator(args.token)
    for result in rotator.keys(usernames_slugs, args.parallelism):
        print(result)
    return 0


def cli() -> int:
    """
    Trawsate's command-line entry point.

    :return: The return code of the program.
    """
    status = main(sys.argv)
    logger.debug('Returning exit status %d', status)
    return status
