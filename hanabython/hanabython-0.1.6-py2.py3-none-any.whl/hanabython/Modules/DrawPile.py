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
from typing import Union
from hanabython.Modules.Colored import Colored
from random import shuffle
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.Card import Card


class DrawPile(Colored, list):
    """
    The draw pile of a game of Hanabi.

    :param cfg: the configuration of the game.

    At initialization, the draw pile is generated with the parameters in
    :attr:`cfg`, then it is shuffled.

    Basically, a DrawPile is a list of cards. The top of the pile, where cards
    are drawn, is represented by the end of the list (not that we care much,
    but it could have an influence someday in some not-yet-implemented
    non-official variants).

    >>> from hanabython.Modules.Configuration import Configuration
    >>> draw_pile = DrawPile(Configuration.STANDARD)
    """

    def __init__(self, cfg: Configuration):
        super().__init__()
        self.cfg = cfg
        for i, c in enumerate(cfg.colors):
            for j, v in enumerate(cfg.values):
                self.extend([Card(c, v)] * cfg.deck[c][j])
        shuffle(self)

    def colored(self) -> str:
        return '[' + ', '.join([card.colored() for card in self]) + ']'

    @property
    def n_cards(self) -> int:
        """
        Number of cards in the pile.

        :return: the number of cards.

        >>> from hanabython.Modules.Configuration import Configuration
        >>> draw_pile = DrawPile(Configuration.STANDARD)
        >>> draw_pile.n_cards
        50
        """
        return len(self)

    def give(self) -> Union[Card, None]:
        """
        Give the card from the top of pile.

        :return: the card drawn. If the pile is empty, return None.

        >>> from hanabython.Modules.Configuration import Configuration
        >>> draw_pile = DrawPile(cfg=Configuration.STANDARD)
        >>> card = draw_pile.give()
        >>> type(card)
        <class 'hanabython.Modules.Card.Card'>
        >>> while draw_pile.n_cards >= 1:
        ...     _ = draw_pile.give()
        >>> print(draw_pile.give())
        None
        """
        if self.n_cards == 0:
            return None
        return self.pop()


if __name__ == '__main__':
    my_draw_pile = DrawPile(cfg=Configuration.W_MULTICOLOR_SHORT)
    my_draw_pile.test_str()

    print('\nDraw a card: ')
    print(my_draw_pile.colored())
    print('n_cards: ', my_draw_pile.n_cards)
    my_card = my_draw_pile.give()
    print(my_card.colored())
    print(my_draw_pile.colored())
    print('n_cards: ', my_draw_pile.n_cards)

    while my_draw_pile.n_cards >= 1:
        my_draw_pile.give()
    print('\nOnce many cards are drawn..')
    print('n_cards: ', my_draw_pile.n_cards)
    print('my_draw_pile.give(): ', my_draw_pile.give())

    import doctest
    doctest.testmod()
