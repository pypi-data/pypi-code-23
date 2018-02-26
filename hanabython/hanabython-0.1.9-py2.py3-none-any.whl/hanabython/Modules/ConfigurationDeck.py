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
from typing import Iterable, Tuple
from hanabython.Modules.Colored import Colored
from hanabython.Modules.Color import Color
from hanabython.Modules.Colors import Colors
from hanabython.Modules.ConfigurationColorContents \
    import ConfigurationColorContents
from collections import OrderedDict


class ConfigurationDeck(Colored, OrderedDict):
    """
    The contents of the deck for a game of Hanabi.

    This is essentially an OrderedDict. To each :class:`Color` in the deck, it
    associates the contents of the color, an object of class
    :class:`ConfigurationColorContents`.

    The order of the colors is important: it will be used in many occasions
    (including for display).

    :param contents: the iterable used to construct the ordered
        dictionary. Typically it is an :class:`OrderedDict` or a list of pairs
        (`color`, `contents`).
    :param name: the name of the configuration. Can be None (default value).
        Should not be capitalized (e.g. "my favorite configuration" and not
        "My favorite configuration").

    >>> cfg = ConfigurationDeck.NORMAL
    >>> print(cfg.name)
    normal
    >>> print(cfg)
    normal
    >>> cfg = ConfigurationDeck(
    ...     contents=[
    ...         (Colors.BLUE, ConfigurationColorContents.NORMAL),
    ...         (Colors.RED, ConfigurationColorContents([3, 2, 1]))
    ...     ]
    ... )
    >>> print(cfg.name)
    None
    >>> print(cfg)
    B normal, R [3, 2, 1]
    """
    def __init__(self,
                 contents: Iterable[Tuple[Color, ConfigurationColorContents]],
                 name: str = None):
        super(ConfigurationDeck, self).__init__(contents)
        self.name = name

    def colored(self) -> str:
        if self.name is None:
            return ', '.join([
                c.color_str('%s %s') % (c, v) for c, v in self.items()
            ])
        else:
            return self.name

    def copy(self) -> 'ConfigurationDeck':
        """
        Copy the deck configuration.

        :return: a copy of this deck configuration. You can modify the copy
            without modifying the original. However, it is not a deep copy,
            (most of time, it would not be useful).

        >>> cfg = ConfigurationDeck.NORMAL.copy()
        >>> cfg.name = None
        >>> del(cfg[Colors.WHITE], cfg[Colors.YELLOW])
        >>> print(cfg)
        B normal, G normal, R normal
        >>> print(ConfigurationDeck.NORMAL[Colors.WHITE])
        normal
        """
        return ConfigurationDeck(contents=self.items(), name=self.name)

    @staticmethod
    def normal_plus(
        contents: Iterable[Tuple[Color, ConfigurationColorContents]],
        name: str = None
    ) -> 'ConfigurationDeck':
        """
        Shortcut to define a deck configuration from the normal one.

        :param contents: the additional contents (typically multicolor, etc.)
        :param name: the name of the configuration.

        :return: the new configuration.

        >>> cfg = ConfigurationDeck.normal_plus(contents=[
        ...     (Colors.SIXTH, ConfigurationColorContents.NORMAL),
        ...     (Colors.MULTICOLOR, ConfigurationColorContents.SHORT)
        ... ])
        >>> print(cfg)
        B normal, G normal, R normal, W normal, Y normal, P normal, M short
        """
        result = ConfigurationDeck.NORMAL.copy()
        result.update(contents)
        result.name = name
        return result

    #: Normal deck (5 colors of 10 cards).
    NORMAL = None
    #: Deck with long sixth color (6 colors of 10 cards).
    W_SIXTH = None
    #: Deck with short sixth color (5 colors of 10 cards + 1 color of 5 cards).
    W_SIXTH_SHORT = None
    #: Deck with long multicolor (5 colors of 10 cards + 1 multi of 10 cards).
    W_MULTICOLOR = None
    #: Deck with short multicolor (5 colors of 10 cards + 1 multi of 5 cards).
    W_MULTICOLOR_SHORT = None
    #: Deck with 8 colors (6 colors + multicolor + colorless, all of 10 cards).
    EIGHT_COLORS = None


ConfigurationDeck.NORMAL = ConfigurationDeck(
    contents=[
        (c, ConfigurationColorContents.NORMAL)
        for c in [Colors.BLUE, Colors.GREEN, Colors.RED,
                  Colors.WHITE, Colors.YELLOW]
    ], name='normal'
)
ConfigurationDeck.W_SIXTH = ConfigurationDeck.normal_plus(
    contents=[(Colors.SIXTH, ConfigurationColorContents.NORMAL)],
    name='with normal sixth color (10 cards)'
)
ConfigurationDeck.W_SIXTH_SHORT = ConfigurationDeck.normal_plus(
    contents=[(Colors.SIXTH, ConfigurationColorContents.SHORT)],
    name='with short sixth color (5 cards)'
)
ConfigurationDeck.W_MULTICOLOR = ConfigurationDeck.normal_plus(
    contents=[(Colors.MULTICOLOR, ConfigurationColorContents.NORMAL)],
    name='with normal multicolor (10 cards)'
)
ConfigurationDeck.W_MULTICOLOR_SHORT = ConfigurationDeck.normal_plus(
    contents=[(Colors.MULTICOLOR, ConfigurationColorContents.SHORT)],
    name='with short multicolor (5 cards)'
)
ConfigurationDeck.EIGHT_COLORS = ConfigurationDeck.normal_plus(
    contents=[
        (Colors.SIXTH, ConfigurationColorContents.NORMAL),
        (Colors.MULTICOLOR, ConfigurationColorContents.NORMAL),
        (Colors.COLORLESS, ConfigurationColorContents.NORMAL)
    ],
    name='with sixth color, multicolor and colorless (10 cards each)'
)


if __name__ == '__main__':
    print('A deck configuration with a name:')
    my_cfg = ConfigurationDeck.W_MULTICOLOR
    my_cfg.test_str()

    print('\nA deck configuration with no name:')
    my_cfg = ConfigurationDeck(
        contents=[
            (Colors.BLUE, ConfigurationColorContents.NORMAL),
            (Colors.RED, ConfigurationColorContents([3, 2, 1]))
        ]
    )
    my_cfg.test_str()

    print('\nChange a part of the configuration:')
    my_cfg[Colors.BLUE] = ConfigurationColorContents([1, 1])
    print(my_cfg.colored())

    print('\nTest the copy method:')
    my_cfg = ConfigurationDeck.NORMAL.copy()
    my_cfg.name = None
    del(my_cfg[Colors.BLUE])
    print('New configuration:', my_cfg.colored())
    print('Blue in the old configuration:',
          ConfigurationDeck.NORMAL[Colors.BLUE])

    import doctest
    doctest.testmod()
