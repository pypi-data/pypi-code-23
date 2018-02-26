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


class ActionThrow(Action):
    """
    An action of a player: throw (discard willingly).

    :param k: position of the card in the hand (between 0 and `#cards - 1`).
        Be careful: as of now, :attr:`__str__` expresses the position in
        "user-friendly" format, i.e. between 1 and `#cards` (this behavior might
        change in the future).

    >>> action = ActionThrow(k=2)
    >>> print(action)
    Discard card in position 3
    """
    def __init__(self, k: int):
        super().__init__(Action.THROW)
        self.k = k

    def colored(self) -> str:
        # Reminded: in end-user interfaces (including ``colored`` methods),
        # we say 'discard'.
        return 'Discard card in position %s' % (self.k + 1)


if __name__ == '__main__':
    my_action = ActionThrow(k=2)
    my_action.test_str()

    import doctest
    doctest.testmod()
