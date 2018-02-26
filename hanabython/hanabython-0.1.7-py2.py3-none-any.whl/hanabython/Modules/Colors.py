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
from hanabython.Modules.StringAnsi import StringAnsi
from hanabython.Modules.Color import Color
from hanabython.Modules.ColorMulticolor import ColorMulticolor
from hanabython.Modules.ColorColorless import ColorColorless


class Colors:
    """
    Standard colors in Hanabi.
    """

    #:
    BLUE = Color(name='Blue', symbol='B', print_color=StringAnsi.BLUE)
    #:
    GREEN = Color(name='Green', symbol='G', print_color=StringAnsi.GREEN)
    #:
    RED = Color(name='Red', symbol='R', print_color=StringAnsi.RED)
    #:
    WHITE = Color(name='White', symbol='W', print_color=StringAnsi.WHITE)
    #:
    YELLOW = Color(name='Yellow', symbol='Y', print_color=StringAnsi.YELLOW)
    #: Use this for the sixth color. As of now, it is pink but the display
    #: color might change in future implementations.
    SIXTH = Color(name='Pink', symbol='P', print_color=StringAnsi.MAGENTA)
    #: Use this for multicolor cards. As of now, it is cyan but the display
    #: color might change in future implementations.
    MULTICOLOR = ColorMulticolor(
        name='Multicolor', symbol='M', print_color=(
            StringAnsi.CYAN + StringAnsi.STYLE_BOLD + StringAnsi.STYLE_UNDERLINE
        )
    )
    #: Use this for the colorless cards. As of now, it is brown but the display
    #: color might change in future implementations.
    COLORLESS = ColorColorless(
        name='Colorless', symbol='C', print_color=(
            StringAnsi.RED + StringAnsi.STYLE_BOLD + StringAnsi.STYLE_UNDERLINE
        )
    )

    @classmethod
    def from_symbol(cls, s: str) -> Color:
        """
        Find one of the standard colors from its symbol.

        :return: the corresponding color.

        >>> color = Colors.from_symbol('B')
        >>> print(color.name)
        Blue
        """
        for k in Colors.__dict__.keys():
            try:
                symbol = Colors.__dict__[k].symbol
            except AttributeError:
                continue
            if symbol == s:
                return Colors.__dict__[k]
        raise ValueError('Could not find color with symbol: ', s)


if __name__ == '__main__':
    Colors.BLUE.test_str()

    my_color = Colors.from_symbol('B')
    print('\n' + my_color.colored())
    try:
        my_color = Colors.from_symbol('Z')
        print(my_color.colored())
    except ValueError as e:
        print(e)

    print('\n' + Colors.BLUE.colored())
    print(Colors.GREEN.colored())
    print(Colors.RED.colored())
    print(Colors.WHITE.colored())
    print(Colors.YELLOW.colored())
    print(Colors.SIXTH.colored())
    print(Colors.MULTICOLOR.colored())
    print(Colors.COLORLESS.colored())

    import doctest
    doctest.testmod()
