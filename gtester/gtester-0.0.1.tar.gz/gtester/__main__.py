#!/usr/bin/env python

"""
    Goban Tester
    Copyright (C) 2018 Berke Emrecan Arslan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import argparse

from gtester import GNU_GO_COMMAND
from gtester.tester import GobanTester

_VERSION = "gtester 0.0.1"


def run(goban_path, goban_args, sgf_file_path, gnugo_path):
    if gnugo_path is not None:
        GNU_GO_COMMAND[0] = gnugo_path
    if goban_args is None:
        goban_args = ''

    tester = GobanTester(
        [goban_path, goban_args.split()],
        GNU_GO_COMMAND,
        sgf_file=sgf_file_path
    )
    tester.run()
    tester.kill_gobans()


if __name__ == "__main__":
    args = argparse.ArgumentParser(
        prog="gtester",
        description="Tests your goban implementation by playing with both "
                    "gnugo and your implementation.",
        version=_VERSION
    )

    args.add_argument(
        "goban_path",
        help="Path to executable of your implementation of goban"
    )

    args.add_argument(
        "--goban_args",
        help="Goban arguments"
    )

    args.add_argument(
        "--gnugo",
        help="Path to gnugo binary",
        default="gnugo"
    )

    args.add_argument(
        "--sgf",
        help="Test board with specific SGF file"
    )

    args.add_argument(
        "--clear-cache",
        help="Deletes downloaded games",
        action='store_true'
    )

    args = args.parse_args()

    if args.clear_cache:
        import os
        import gtester.sgf as sgflib

        _, games_file = sgflib.sgf_paths()
        if os.path.exists(games_file):
            os.unlink(games_file)
        print('Cache cleared.')

    run(args.goban_path, args.goban_args, args.sgf, args.gnugo)
