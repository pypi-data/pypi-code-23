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
from hanabython.Modules.Action import Action
from hanabython.Modules.Clue import Clue


class ActionClue(Action):
    """
    An action of a player: give a clue.

    :param i: the relative position of the concerned player
        (i.e. 1 for next player, 2 for second next player, etc.).
    :param clue: the clue.

    >>> from hanabython import Colors
    >>> action = ActionClue(i=1, clue=Clue(2))
    >>> print(action)
    Clue 2 to player in relative position 1
    >>> action = ActionClue(i=2, clue=Clue(Colors.BLUE))
    >>> print(action)
    Clue B to player in relative position 2
    """

    def __init__(self, i: int, clue: Clue):
        super().__init__(Action.CLUE)
        self.i = i
        self.clue = clue

    def colored(self) -> str:
        return 'Clue %s to player in relative position %s' % (
            self.clue.colored(), self.i)


if __name__ == '__main__':
    my_action = ActionClue(i=1, clue=Clue(3))
    my_action.test_str()

    print()
    from hanabython.Modules.Colors import Colors
    my_action = ActionClue(i=1, clue=Clue(Colors.BLUE))
    my_action.test_str()

    import doctest
    doctest.testmod()
