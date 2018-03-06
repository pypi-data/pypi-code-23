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


class GobanNotExists(Exception):
    """
    Raised when requested goban is not existing.
    """

    def __init__(self, *args):
        super(GobanNotExists, self).__init__(*args)


class InvalidGTPResponse(Exception):
    """
    Raised when a goban returned a invalid response
    """

    def __init__(self, *args):
        super(InvalidGTPResponse, self).__init__(*args)


class GTPMetaMachine:
    """
    Communicates with gobans
    """

    def __init__(self):
        self.gobans = {}

    def register_goban(self, process):
        """
        Registers a new goban process to registry.
        :param process:
        :return: generated id of goban
        """
        id = len(list(self.gobans.keys())) + 1
        self.gobans[id] = process

        return id

    def send(self, goban_id, command, reverse_colors=False):
        """
        Sends a command to goban identified by goban_id and returns response
        from goban
        :param goban_id:
        :param command:
        :param reverse_colors:
        :return:
        """
        try:
            goban = self.gobans[goban_id]
        except KeyError:
            raise GobanNotExists

        if reverse_colors:
            command = command.split()
            if command[0] == 'play':
                command[1] = 'W' if command[1] == 'B' else 'B'
            command = ' '.join(command)

        goban.stdin.write(command)
        goban.stdin.write('\n')
        goban.stdin.flush()

        response = self._read_stream(goban.stdout)
        return self._process_response(response)

    @staticmethod
    def _process_response(response):
        """
        Clears unnecessary data
        :param response:
        :return:
        """
        # remove "="
        if response[0] == "=":
            response = response[1:]
        else:
            print(response)
            raise InvalidGTPResponse

        return response.strip()

    @staticmethod
    def _read_stream(stream):
        """
        Reads a stream until encountering a pair of line feed.
        :param stream:
        :return:
        """
        out = ""
        linefeed_seen = False
        while True:
            char = stream.read(1)
            out += char
            if linefeed_seen and char == '\n':
                break
            linefeed_seen = char == '\n'

        return out.strip()
