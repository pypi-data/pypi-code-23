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


class Action(Colored):
    """
    An action performed by a player (Throw, Play a card, Clue or Forfeit).

    In the end-user interfaces (including methods ``colored``), "throw" should
    be called "discard" and "play a card" can be called "play" (to be consistent
    with the official rules). In the code however, we prefer to use "throw"
    (to distinguish from other forms of discards, for example after a misfire)
    and "play a card" (to distinguish from simply playing in general).

    :param category: can be :attr:`Action.THROW`, :attr:`Action.PLAY_CARD`,
        :attr:`Action.CLUE` or :attr:`Action.FORFEIT`.

    Generally, only subclasses are instantiated. Cf. :class:`ActionThrow`,
    :class:`ActionPlayCard`, :class:`ActionClue` and :class:`ActionForfeit`.
    """

    #:
    THROW = 0
    #:
    PLAY_CARD = 1
    #:
    CLUE = 2
    #:
    FORFEIT = 3
    #: Possibles categories of action.
    CATEGORIES = {THROW, PLAY_CARD, CLUE, FORFEIT}

    def __init__(self, category: int):
        if category not in Action.CATEGORIES:
            raise ValueError('Unknown action category: ', category)
        self.category = category
