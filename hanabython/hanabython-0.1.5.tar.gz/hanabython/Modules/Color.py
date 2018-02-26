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
from hanabython.Modules.Colored import Colored
from hanabython.Modules.StringAnsi import StringAnsi


class Color(Colored):
    r"""
    A color in Hanabi.

    :param name: The full name of the color. In a game, two distinct
        colors must have different names.
    :param symbol: The short name of the color. For standard colors
        (defined as constants in :class:`Colors`), it is always 1 character,
        and no two standard colors have the same symbol. For user-defined
        colors, it is recommended to do the same, but not necessary.
    :param print_color: an ANSI escape code that modifies the printing
        color. See :class:`StringAnsi`.

    >>> brown = Color(name='Brown', symbol='N', print_color=StringAnsi.BROWN)
    >>> brown.name
    'Brown'
    >>> brown.symbol
    'N'
    >>> brown.print_color
    '\x1b[33m'
    """

    def __init__(self, name: str, symbol: str, print_color: str):
        self.name = name
        self.symbol = symbol
        self.print_color = print_color

    def colored(self) -> str:
        return self.color_str(self.symbol)

    def color_str(self, o: object) -> str:
        r"""
        Convert an object to a colored string.

        :param o: any object.

        :return: the ``__str__`` of this object, with an ANSI color-modifying
            escape code at the beginning and its cancellation at the end.

        >>> brown = Color(name='Brown', symbol='N',
        ...               print_color=StringAnsi.BROWN)
        >>> brown.color_str('some text')
        '\x1b[33msome text\x1b[0;0m'
        >>> brown.color_str(42)
        '\x1b[33m42\x1b[0;0m'
        """
        return self.print_color + str(o) + StringAnsi.RESET

    def __eq__(self, other):
        return isinstance(other, Color) and (
            (self.name, self.symbol, self.print_color)
            == (other.name, other.symbol, other.print_color)
        )

    def __hash__(self):
        return hash((self.name, self.symbol, self.print_color))

    def match(self, clue_color: 'Color') -> bool:
        """
        React to a color clue.

        :param clue_color: the color of the clue.

        :return: whether a card of the current color should react to a clue of
            color :attr:`clue_color`. A normal color matches simply if the color
            of the clue is the same. This is different in
            :class:`ColorMulticolor` and :class:`ColorColorless`.

        >>> brown = Color(name='Brown', symbol='N',
        ...               print_color=StringAnsi.BROWN)
        >>> pink = Color(name='Pink', symbol='P',
        ...              print_color=StringAnsi.MAGENTA)
        >>> brown.match(clue_color=brown)
        True
        >>> brown.match(clue_color=pink)
        False
        """
        return self == clue_color

    @property
    def is_cluable(self):
        """
        :return: whether this color can be used for clues. For a normal color,
            it is True. This is different in
            :class:`ColorMulticolor` and :class:`ColorColorless`.
        """
        return True


if __name__ == '__main__':
    brown = Color(name='Brown', symbol='N', print_color=StringAnsi.BROWN)
    brown.test_str()

    pink = Color(name='Pink', symbol='P', print_color=StringAnsi.MAGENTA)
    pseudo_pink = Color(name='Pink', symbol='P', print_color=StringAnsi.MAGENTA)

    print('pseudo_pink == pink: ', pseudo_pink == pink)
    my_set = {brown, pink}
    print('In the set = ', pseudo_pink in my_set)
    my_dict = {brown: 'a', pink: 'b'}
    print('In the dict = ', pseudo_pink in my_dict.keys())
    print('my_dict[pseudo_pink] = ', my_dict[pseudo_pink])

    import doctest
    doctest.testmod()
