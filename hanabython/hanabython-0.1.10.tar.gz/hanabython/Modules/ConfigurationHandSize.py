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
from typing import Callable
from hanabython.Modules.Colored import Colored


class ConfigurationHandSize(Colored):
    """
    A rule for the initial size of the players' hands.

    :param f: a callable that, to a number of players, associates a number of
        cards.
    :param name: the name of the configuration. Can be None (default value).
        Should not be capitalized (e.g. "my favorite configuration" and not
        "My favorite configuration").

    >>> cfg = ConfigurationHandSize.NORMAL
    >>> print(cfg)
    normal
    >>> cfg = ConfigurationHandSize(f=lambda n: 9 - n)
    >>> print(cfg)
    7 for 2p, 6 for 3p, 5 for 4p, 4 for 5p
    """

    def __init__(self, f: Callable[[int], int], name: str = None):
        self.f = f
        self.name = name

    def colored(self) -> str:
        if self.name is None:
            return ', '.join([
                '%s for %sp' % (self.f(n), n) for n in range(2, 6)
            ])
        else:
            return self.name

    #: Normal rule for hand size (5 for 3- players, 4 for 4+ players).
    NORMAL = None
    #: Experimental variant for hand size (6 for 2 players, 3 for 5+ players).
    VARIANT_6_3 = None


ConfigurationHandSize.NORMAL = ConfigurationHandSize(
    f=lambda n: 5 if n <= 3 else 4,
    name='normal'
)
ConfigurationHandSize.VARIANT_6_3 = ConfigurationHandSize(
    f=lambda n: 3 if n >= 5 else 8 - n,
    name='experimental (6 for 2 players, 3 for 5 players)'
)


if __name__ == '__main__':
    print('A configuration with a name:')
    my_cfg = ConfigurationHandSize.NORMAL
    my_cfg.test_str()

    print('\nA configuration with no name:')
    my_cfg = ConfigurationHandSize(f=lambda n: 9 - n)
    my_cfg.test_str()

    import doctest
    doctest.testmod()
