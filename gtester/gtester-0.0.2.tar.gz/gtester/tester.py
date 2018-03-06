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

import gtester.sgf as sgflib
from gtester.gtp import GTPMetaMachine, InvalidGTPResponse
from gtester.taskmaster import start_process
from gtester.parser import GnuGoParser


class GobanTester:
    def __init__(self, goban_1, goban_2, goban_1_parser=None,
                 goban_2_parser=None,
                 sgf_file=None,
                 sgf_str=None):
        self.meta = GTPMetaMachine()

        # start gobans and register to meta
        goban_1 = start_process(goban_1[0], goban_1[1])
        goban_2 = start_process(goban_2[0], goban_2[1])
        self.goban_1 = self.meta.register_goban(goban_1)
        self.goban_2 = self.meta.register_goban(goban_2)

        if goban_1_parser is not None:
            self.goban_1_parser = goban_1_parser
        else:
            self.goban_1_parser = GnuGoParser()

        if goban_2_parser is not None:
            self.goban_2_parser = goban_2_parser
        else:
            self.goban_2_parser = GnuGoParser()

        # ====
        if sgf_file is not None:
            self.games = [sgflib.parse_file(sgf_file)]
        elif sgf_str is not None:
            self.games = [sgflib.parse(sgf_str)]
        else:
            self.games = [
                sgflib.parse(f)
                for f in sgflib.sgf_download()
            ]

        self.games = [
            sgflib.sgf2gtp(sgf)
            for sgf in self.games
        ]

    def run(self):
        error_occured = False
        for reverse_color in [False, True]:
            for i, game in enumerate(self.games):
                for goban in [self.goban_1, self.goban_2]:
                    self.meta.send(goban, 'clear_board')

                print('Game {:-2d}/{}'.format(i + 1, len(self.games)), end=' ')
                game_length = len(game)
                for j, cmd in enumerate(game):
                    if j % (game_length / 10) == 0:
                        print('.', end='')

                    for goban in [self.goban_1, self.goban_2]:
                        try:
                            self.meta.send(goban, cmd,
                                           reverse_colors=reverse_color)
                        except InvalidGTPResponse as e:
                            print(cmd)
                            raise e

                result = [
                    self.meta.send(goban, 'showboard')
                    for goban in [self.goban_1, self.goban_2]
                ]

                result = self._compare_boards(result[0], result[1])
                if len(result) > 0:
                    print('Oops!')
                    error_occured = True
                else:
                    print('OK')

            if not error_occured:
                print('Reversing colors ..')

        if not error_occured:
            print('All test passed.')

    def kill_gobans(self):
        for goban in [self.goban_1, self.goban_2]:
            self.meta.send(goban, 'quit')

    def _compare_boards(self, board_1, board_2):
        """
        Compares boards and returns different indexes
        :param board_1:
        :param board_2:
        :return:
        """
        board_1 = self.goban_1_parser.parse(board_1)
        board_2 = self.goban_2_parser.parse(board_2)

        board_1 = [ord(c) for c in board_1]
        board_2 = [ord(c) for c in board_2]

        out = [
            b1 - b2
            for b1, b2 in zip(board_1, board_2)
        ]

        return [i for i, e in enumerate(out) if e != 0]
