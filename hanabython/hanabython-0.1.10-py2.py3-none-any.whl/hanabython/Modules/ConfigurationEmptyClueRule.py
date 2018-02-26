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


class ConfigurationEmptyClueRule(Colored):
    """
    A rule for "empty clues" in Hanabi.

    An empty clue is a clue that corresponds to 0 cards in the hand of the
    concerned partner.

    This class does not implement the rules themselves: they are hardcoded in
    the class :class:`Game`.

    :param i: a unique identifier of the rule.
    :param name: the name of the configuration.
        Should not be capitalized (e.g. "my favorite configuration" and not
        "My favorite configuration").

    >>> cfg = ConfigurationEmptyClueRule.FORBIDDEN
    >>> print(cfg)
    empty clues are forbidden
    >>> print(cfg==ConfigurationEmptyClueRule.FORBIDDEN)
    True
    >>> print(cfg==ConfigurationEmptyClueRule.ALLOWED)
    False
    """

    def __init__(self, i: int, name: str):
        self.i = i
        self.name = name

    def colored(self) -> str:
        return self.name

    def __eq__(self, other: 'ConfigurationEmptyClueRule') -> bool:
        return self.i == other.i

    #:
    FORBIDDEN = None
    #:
    ALLOWED = None


ConfigurationEmptyClueRule.FORBIDDEN = ConfigurationEmptyClueRule(
    0, 'empty clues are forbidden')
ConfigurationEmptyClueRule.ALLOWED = ConfigurationEmptyClueRule(
    1, 'empty clues are allowed')


if __name__ == '__main__':
    cfg = ConfigurationEmptyClueRule.ALLOWED
    cfg.test_str()

    print('\nIs it allowed?', cfg == ConfigurationEmptyClueRule.ALLOWED)
    print('Is it forbidden?', cfg == ConfigurationEmptyClueRule.FORBIDDEN)

    import doctest
    doctest.testmod()
