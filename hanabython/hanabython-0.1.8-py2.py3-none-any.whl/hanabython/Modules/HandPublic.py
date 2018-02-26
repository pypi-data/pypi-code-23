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
from typing import List
from hanabython.Modules.Colors import Colors
from hanabython.Modules.Clue import Clue
from hanabython.Modules.Colored import Colored
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.CardPublic import CardPublic


class HandPublic(Colored, list):
    """
    The "public" part of a hand.

    An object of this class represents what is known by all players, including
    the owner of the hand.

    We use the same convention as in Board Game Arena: newest cards are on the
    left (i.e. at the beginning of the list) and oldest cards are on the right
    (i.e. at the end of the list).

    Basically, a HandPublic is a list of CardPublic objects.

    :param cfg: the configuration of the game.
    :param n_cards: the number of cards in the hand. N.B.: this parameter
        is mostly used for examples and tests. In contrast, at the beginning of
        a game, the hand should be initialized with 0 cards, because cards will
        be given one by one to the players during the initial dealing of hands.

    >>> hand = HandPublic(cfg=Configuration.STANDARD, n_cards=4)
    >>> print(hand)
    BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345
    """
    def __init__(self, cfg: Configuration, n_cards: int = 0):
        super().__init__()
        self.cfg = cfg
        for i in range(n_cards):
            self.receive()

    def colored(self) -> str:
        return ', '.join([card.colored() for card in self])

    def receive(self) -> None:
        """
        Receive a card.

        An unknown card is added on the left, i.e. at the beginning of the list.

        >>> hand = HandPublic(cfg=Configuration.STANDARD, n_cards=4)
        >>> hand.match(clue=Clue(5), bool_list=[True, True, False, False])
        >>> print(hand)  #doctest: +NORMALIZE_WHITESPACE
        BGRWY 5  ,   BGRWY 5  , BGRWY 1234 , BGRWY 1234
        >>> hand.receive()
        >>> print(hand)  #doctest: +NORMALIZE_WHITESPACE
        BGRWY 12345,   BGRWY 5  ,   BGRWY 5  , BGRWY 1234 , BGRWY 1234
        """
        self.insert(0, CardPublic(self.cfg))

    def give(self, k: int) -> None:
        """
        Give a card.

        :param k: the position of the card in the hand (0 = newest).

        The card is simply suppressed from the hand.

        >>> hand = HandPublic(cfg=Configuration.STANDARD, n_cards=4)
        >>> hand.match(clue=Clue(5), bool_list=[False, True, False, False])
        >>> hand.match(clue=Clue(4), bool_list=[True, False, False, False])
        >>> print(hand)  #doctest: +NORMALIZE_WHITESPACE
        BGRWY 4  ,   BGRWY 5  ,  BGRWY 123 ,  BGRWY 123
        >>> hand.give(1)
        >>> print(hand)  #doctest: +NORMALIZE_WHITESPACE
        BGRWY 4  ,  BGRWY 123 ,  BGRWY 123
        """
        self.pop(k)

    def match(self, clue: Clue, bool_list: List[bool]):
        """
        React to a clue

        :param clue: the clue.
        :param bool_list: a list of booleans. The `i`-th coefficient is
            `True` iff the `i`-th card of the hand matches the clue given.

        Updates the internal variables of the hand.

        >>> hand = HandPublic(cfg=Configuration.STANDARD, n_cards=4)
        >>> hand.match(clue=Clue(3), bool_list=[False, True, False, False])
        >>> print(hand)  #doctest: +NORMALIZE_WHITESPACE
        BGRWY 1245 ,   BGRWY 3  , BGRWY 1245 , BGRWY 1245
        >>> hand.match(clue=Clue(Colors.RED),
        ...            bool_list=[False, True, False, False])
        >>> print(hand)  #doctest: +NORMALIZE_WHITESPACE
        BGWY 1245 ,     R3     ,  BGWY 1245 ,  BGWY 1245
        """
        for i, card in enumerate(self):
            card.match(clue=clue, b=bool_list[i])


if __name__ == '__main__':
    my_hand = HandPublic(cfg=Configuration(), n_cards=4)
    my_hand.test_str()

    print("\nLet's give some clues: ")
    print(my_hand.colored())
    my_hand.match(clue=Clue(Colors.RED),
                  bool_list=[True, False, True, False, False])
    print(my_hand.colored())
    my_hand.match(clue=Clue(Colors.BLUE),
                  bool_list=[False, True, False, False, False])
    print(my_hand.colored())
    my_hand.match(clue=Clue(3),
                  bool_list=[True, False, False, True, False])
    print(my_hand.colored())

    print("\nGive card in position 2: ")
    my_hand.give(2)
    print(my_hand.colored())
    print("Receive a new card: ")
    my_hand.receive()
    print(my_hand.colored())

    import doctest
    doctest.testmod()
