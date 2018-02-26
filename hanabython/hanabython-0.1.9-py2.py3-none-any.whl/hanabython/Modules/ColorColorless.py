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
from hanabython.Modules.Color import Color
from hanabython.Modules.StringAnsi import StringAnsi


class ColorColorless(Color):

    def match(self, clue_color: Color) -> bool:
        """
        Colorless matches no color clue.

        >>> colorless = ColorColorless(name='Colorless', symbol='C',
        ...                            print_color=StringAnsi.MAGENTA)
        >>> brown = Color(name='Brown', symbol='N',
        ...               print_color=StringAnsi.BROWN)
        >>> colorless.match(clue_color=brown)
        False
        """
        return False

    @property
    def is_cluable(self):
        """
        :return: False. It is not allowed to give "colorless" as a clue.
        """
        return False


if __name__ == '__main__':
    import doctest
    doctest.testmod()
