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
import re
from typing import Iterable


def uncolor(s: str) -> str:
    """
    Remove ANSI escape codes from the string.

    :param string s: a string.

    :return: the same string without its ANSI escape codes.

    >>> from hanabython import StringAnsi
    >>> s = (StringAnsi.RED + "Hanabi" + StringAnsi.RESET + ', a game by '
    ...      + StringAnsi.BLUE + 'Antoine Bauza' + StringAnsi.RESET)
    >>> uncolor(s)
    'Hanabi, a game by Antoine Bauza'
    """
    return re.sub(r'\033.\d*(;\d*)?m', "", s)


def title(s: str, width: int) -> str:
    """
    Format a string as a title.

    :param s: the string
    :param width: the total width of the final layout (in number of
        characters).

    :return: the string formatted as a title.

    >>> title(s='Title', width=20)
    '****** Title *******'
    >>> title(s='A not-too-long title', width=20)
    'A not-too-long title'
    >>> title(s='A title that is really too long', width=20)
    'A title that is r...'
    """
    if len(s) > width:
        return s[:width - 3] + '...'
    if len(s) > width - 2:
        return s.ljust(width)
    left = (width - len(s)) // 2
    right = width - len(s) - left
    return '*' * (left - 1) + ' ' + s + ' ' + '*' * (right - 1)


def str_from_iterable(l: Iterable) -> str:
    """
    Convert an iterable to a simple string.

    There are two differences with the standard implementation of str:

    #. No brackets.
    #. For each ``item`` of the iterable, ``str_from_iterable`` uses
       ``str(item)``, whereas ``str`` uses ``repr(item)``.

    :param l: an iterable.
    :return: a simple string.

    >>> print(str_from_iterable(['a', 'b', 'c']))
    a b c
    >>> print(['a', 'b', 'c'])
    ['a', 'b', 'c']
    """
    return ' '.join([str(x) for x in l])


if __name__ == "__main__":
    my_s = "\033[0;31mHanabi\033[0;0m by \033[0;94mAntoine Bauza\033[0;0m"
    print(my_s)
    print(uncolor(my_s))

    print()
    print(title(s='Title', width=20))
    print(title(s='123456789012345678', width=20))
    print(title(s='1234567890123456789', width=20))
    print(title(s='12345678901234567890', width=20))
    print(title(s='123456789012345678901', width=20))
    print(title(s='A title that is really too long', width=20))

    print()
    print(str_from_iterable(['a', 'b', 'c']))
    print(['a', 'b', 'c'])

    import doctest
    doctest.testmod()
