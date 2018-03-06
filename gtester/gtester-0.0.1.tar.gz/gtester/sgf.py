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

import re
import os
import pickle
import random
import requests

from bs4 import BeautifulSoup

from gtester import GNU_GO_COMMAND
from gtester.gtp import InvalidGTPResponse

_SGF_PATTERN = "([\w]+)[[]([a-z0-9\sA-Z\.-]+)[]]"
_VALID_SGF_COMMANDS = [
    'B', 'W', 'SZ', 'RE'
    # move by black, move by white
    # board size, game result
]
_GNU_GO_VERTICAL_COORDINATES = "A B C D E F G H J K L M N O P Q R S T".split()
_SGF_SOURCE = 'http://gokifu.com/index.php'
_GAME_COUNT = 10


def sgf_paths():
    data_dir = os.path.join(os.path.expanduser('~'), '.gtester')
    games_file = os.path.join(data_dir, 'games.dat')

    return data_dir, games_file


def sgf_download():
    """
    Downloads random SGF files for testing gobans
    :return:
    """
    # check if ~/.gtester exists, or create it
    data_dir, games_file = sgf_paths()
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(games_file):
        from gtester.tester import GobanTester
        print('There is no cached games, downloading ..')

        r = []
        error = True
        while error:
            error = False

            r = requests.get(_SGF_SOURCE).text
            r = BeautifulSoup(r, 'html.parser')
            r = r.find_all('div', {'class': 'player_block cblock_3'})
            r = [rr.find_all('a')[3]['href'] for rr in r]

            print('Downloaded game index, choosing {} games randomly ..'.format(
                _GAME_COUNT))
            r = [random.choice(r) for _ in range(_GAME_COUNT)]
            r = [requests.get(rr).text.encode('ascii', 'ignore') for rr in r]

            print('Checking games for illegal moves ..')
            for rr in r:
                tester = GobanTester(GNU_GO_COMMAND, GNU_GO_COMMAND, sgf_str=rr)

                try:
                    tester.run()
                except InvalidGTPResponse:
                    error = True
                    print('Encountered illegal played game, redownloading ..')
                tester.kill_gobans()

        print('Done. Writing downloaded games to cache ({}) ..'.format(
            games_file))
        games_file = open(games_file, 'w')
        pickle.dump(r, games_file)
    else:
        print('Found cached games, reading from cache ..')
        games_file = open(games_file, 'r')
        r = pickle.load(games_file)

    games_file.close()
    return r


def _coord_sgf2gtp(sgf_coordinate):
    x, y = sgf_coordinate[0], sgf_coordinate[1]
    x, y = ord(x), ord(y)

    return '{}{}'.format(
        _GNU_GO_VERTICAL_COORDINATES[x - ord('a')],
        y - ord('a') + 1
    )


def sgf2gtp(sgf_commands):
    """
    Converts a SGF command to GTP command
    :param sgf_commands:
    :return:
    """
    sgf_commands = filter_commands(sgf_commands)
    for i, cmd in enumerate(sgf_commands):
        sgf_commands[i][1] = [sgf_commands[i][1]]

        if cmd[0] in ['B', 'W']:
            sgf_commands[i][1][0] = _coord_sgf2gtp(sgf_commands[i][1][0])
            sgf_commands[i][1].insert(0, cmd[0])
            sgf_commands[i][0] = 'play'
        elif cmd[0] == 'SZ':
            sgf_commands[i][0] = 'boardsize'

        sgf_commands[i] = ' '.join(
            [sgf_commands[i][0], ' '.join(sgf_commands[i][1])]
        )

    return sgf_commands


def filter_commands(sgf_commands):
    """
    Filters commands
    :param sgf_commands:
    :return:
    """
    return [
        cmd
        for cmd in sgf_commands
        if cmd[0] in _VALID_SGF_COMMANDS
    ]


def parse(text):
    """
    Extracts commands and parameters from SGF string
    :param text:
    :return:
    """
    all_matches = re.findall(_SGF_PATTERN, text)
    for i, match in enumerate(all_matches):
        all_matches[i] = list(match)

    return all_matches


def parse_file(file_path):
    """
    Reads SGF data from file and returns parsed commands and parameters
    :param file_path:
    :return:
    """
    f = open(file_path)
    sgf = ''.join(f.readlines())
    f.close()

    return parse(sgf)
