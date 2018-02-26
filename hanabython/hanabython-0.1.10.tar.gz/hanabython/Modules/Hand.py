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
from typing import Iterable, Union, List
from hanabython.Modules.Clue import Clue
from hanabython.Modules.Colored import Colored
from hanabython.Modules.Card import Card
from hanabython.Modules.Colors import Colors


class Hand(Colored, list):
    """
    The hand of a player.

    We use the same convention as in Board Game Arena: newest cards are on the
    left (i.e. at the beginning of the list) and oldest cards are on the right
    (i.e. at the end of the list).

    Basically, a Hand is a list of Card objects. It can be constructed as such,
    or using a list of strings which will be automatically converted to cards.

    :param source: an iterable used to construct the hand. N.B.: this parameter
        is mostly used for examples and tests. In contrast, at the beginning of
        a game, the hand should be initialized with no cards, because cards will
        be given one by one to the players during the initial dealing of hands.

    >>> hand = Hand([Card('Y3'), Card('M1'), Card('B2'), Card('R4')])
    >>> print(hand)
    Y3 M1 B2 R4
    >>> hand = Hand(['Y3', 'M1', 'B2', 'R4'])
    >>> print(hand)
    Y3 M1 B2 R4
    """
    def __init__(self, source: Iterable[Union[Card, str]] = None):
        super().__init__()
        if source is not None:
            for item in source:
                if type(item) == str:
                    self.append(Card(item))
                else:
                    self.append(item)

    def colored(self) -> str:
        return ' '.join(card.colored() for card in self)

    def receive(self, card: Card) -> None:
        """
        Receive a card.

        :param card: the card received.

        The card is added on the left, i.e. at the beginning of the list.

        >>> hand = Hand(['Y3', 'M1', 'B2', 'R4'])
        >>> hand.receive(Card('G2'))
        >>> print(hand)
        G2 Y3 M1 B2 R4
        """
        self.insert(0, card)

    def give(self, k: int) -> Card:
        """
        Give a card.

        :param k: the position of the card in the hand (0 = newest).

        :return: the card given.

        >>> hand = Hand(['Y3', 'B1', 'M1', 'B2', 'R4'])
        >>> card = hand.give(1)
        >>> print(card)
        B1
        >>> print(hand)
        Y3 M1 B2 R4
        """
        return self.pop(k)

    def match(self, clue: Clue) -> List[bool]:
        """
        React to a clue.

        :param clue: the clue.

        :return: a list of booleans. The `i`-th coefficient is `True`
            iff the `i`-th card of the hand matches the clue given.

        >>> hand = Hand(['G2', 'Y3', 'M1', 'B2', 'R4'])
        >>> hand.match(Clue(Colors.RED))
        [False, False, True, False, True]
        >>> hand.match(Clue(2))
        [True, False, False, True, False]
        """
        return [card.match(clue) for card in self]


if __name__ == '__main__':
    my_hand = Hand(['Y3', 'B1', 'M1', 'B2', 'R4'])
    my_hand.test_str()

    my_card = my_hand.give(1)
    print('\nCard given: ', my_card.colored())
    print(my_hand.colored())

    my_card = Card('G2')
    my_hand.receive(my_card)
    print('\nCard received: ', my_card.colored())
    print(my_hand.colored())

    print('\nMatch red clue:')
    print(my_hand.match(Clue(Colors.RED)))

    print('\nMatch clue 2:')
    print(my_hand.match(Clue(2)))
    # print(hand.bool_list_from_clue(Action(
    #     category=Action.INFORM, clue_type=Action.VALUE, clue=2
    # )))

    import doctest
    doctest.testmod()
