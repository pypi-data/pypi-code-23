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


class ConfigurationEndRule(Colored):
    """
    A rule for the end of game in Hanabi.

    This class does not implement the rules themselves: they are hardcoded in
    the class :class:`Game`.

    :param i: a unique identifier of the rule.
    :param name: the name of the configuration.
        Should not be capitalized (e.g. "my favorite configuration" and not
        "My favorite configuration"), except if it is seen as a title
        (e.g. "Crowning Piece").

    >>> cfg = ConfigurationEndRule.NORMAL
    >>> print(cfg)
    normal
    >>> print(cfg==ConfigurationEndRule.NORMAL)
    True
    >>> print(cfg==ConfigurationEndRule.CROWNING_PIECE)
    False
    """

    def __init__(self, i: int, name: str):
        self.i = i
        self.name = name

    def colored(self) -> str:
        return self.name

    def __eq__(self, other: 'ConfigurationEndRule') -> bool:
        return self.i == other.i

    #: Default rule for the end of game. When a player draws the last card,
    #: all players play one last time (her included).
    NORMAL = None
    #: "Crowning piece" variant for the end of game. The game stops when a
    #: player starts her turn with no card in hand.
    CROWNING_PIECE = None


ConfigurationEndRule.NORMAL = ConfigurationEndRule(0, 'normal')
ConfigurationEndRule.CROWNING_PIECE = ConfigurationEndRule(1, 'Crowning Piece')


if __name__ == '__main__':
    cfg = ConfigurationEndRule.NORMAL
    cfg.test_str()

    print('\nIs it normal?', cfg == ConfigurationEndRule.NORMAL)
    print('Is it Crowning Piece?', cfg == ConfigurationEndRule.CROWNING_PIECE)

    import doctest
    doctest.testmod()
