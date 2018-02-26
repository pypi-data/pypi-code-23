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
from typing import Union
from hanabython.Modules.Colored import Colored
from hanabython.Modules.Color import Color
from hanabython.Modules.Colors import Colors


class Clue(Colored):
    """
    A clue.

    :param x: the clue (value or color).

    :var int category: can be either Clue.VALUE or Clue.COLOR.

    >>> clue = Clue(1)
    >>> print(clue)
    1
    >>> clue.category == Clue.VALUE
    True
    >>> clue = Clue(Colors.RED)
    >>> print(clue)
    R
    >>> clue.category == Clue.COLOR
    True
    """

    #: Category for a clue by value.
    VALUE = 0
    #: Category for a clue by color.
    COLOR = 1

    def __init__(self, x: Union[int, Color]):
        self.x = x
        self.category = Clue.VALUE if type(x) == int else Clue.COLOR

    def colored(self) -> str:
        if self.category == self.VALUE:
            return str(self.x)
        else:
            return self.x.colored()


if __name__ == '__main__':
    my_clue = Clue(1)
    my_clue.test_str()
    print()
    my_clue = Clue(Colors.BLUE)
    my_clue.test_str()

    import doctest
    doctest.testmod()
