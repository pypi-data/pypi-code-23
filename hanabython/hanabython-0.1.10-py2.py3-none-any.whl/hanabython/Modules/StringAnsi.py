# -*- coding: utf-8 -*-
"""
Copyright François Durand
fradurand@gmail.com

This file is part of Hanabython.

    Hanabython is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Hanabython is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Hanabython.  If not, see <http://www.gnu.org/licenses/>.
"""


class StringAnsi:
    """
    An ANSI escape code that modifies the printing aspect.
    """

    #: This escape code is special: it is used to return to default aspect.
    RESET = "\033[0;0m"
    #:
    STYLE_BOLD = "\033[1m"
    #:
    STYLE_UNDERLINE = "\033[4m"
    #:
    STYLE_REVERSE_VIDEO = "\033[7m"

    WHITE_NOT_BRIGHT = "\033[30m"
    WHITE_BRIGHT = "\033[90m"
    #: This should be white on black background, and vice-versa.
    WHITE = ""

    RED_NOT_BRIGHT = "\033[31m"
    RED_BRIGHT = "\033[91m"
    #:
    RED = RED_NOT_BRIGHT

    GREEN_NOT_BRIGHT = "\033[32m"
    GREEN_BRIGHT = "\033[92m"
    #:
    GREEN = GREEN_NOT_BRIGHT

    YELLOW_NOT_BRIGHT = "\033[33m"
    YELLOW_BRIGHT = "\033[93m"
    #:
    YELLOW = YELLOW_BRIGHT
    #:
    BROWN = YELLOW_NOT_BRIGHT

    BLUE_NOT_BRIGHT = "\033[34m"
    BLUE_BRIGHT = "\033[94m"
    #:
    BLUE = BLUE_BRIGHT

    MAGENTA_NOT_BRIGHT = "\033[35m"
    MAGENTA_BRIGHT = "\033[95m"
    #:
    MAGENTA = MAGENTA_NOT_BRIGHT

    CYAN_NOT_BRIGHT = "\033[36m"
    CYAN_BRIGHT = "\033[96m"
    #:
    CYAN = CYAN_BRIGHT


if __name__ == '__main__':
    # N.B.: Available colors for multi are brown, magenta and cyan
    for k in StringAnsi.__dict__.keys():
        if not k.startswith('_'):
            print(StringAnsi.__dict__[k] + k + StringAnsi.RESET)
