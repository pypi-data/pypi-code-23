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
import numpy as np
from hanabython.Modules.Colored import Colored
from hanabython.Modules.StringUtils import uncolor, str_from_iterable
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.Card import Card


class DiscardPile(Colored):
    """
    The discard pile in a game of Hanabi.

    :param cfg: the configuration of the game.

    :var list chronological: a list a cards discarded, by chronological order.
    :var np.array array: each row represents a color, each column a card value.
        The coefficient is the number of copies of this card in the discard
        pile.
    :var np.array not_discarded: is equal to :attr:`Configuration.deck_array`
        - :attr:`array`. Number of copies left for each card (including
        everything except the discard pile: the draw pile, the players' hand and
        the board).
    :var np.array scorable: each row represents a color, each column a
        card value. The coefficient is True it is possible to have a such
        card on the board at the end of the game (whether it is already on the
        board or not). For example, if the two G4's are discarded, then G4 and
        G5 are not "scorable". Note that a 1 always is considered "scorable",
        whether it is on the board or not.

    >>> from hanabython import Configuration
    >>> discard_pile = DiscardPile(Configuration.STANDARD)
    >>> print(discard_pile)
    No card discarded yet

    Check that scorable cards are counted correctly with unusual configurations:

    >>> from hanabython import (Configuration, ConfigurationDeck,
    ...                         Colors, ConfigurationColorContents)
    >>> discard_pile = DiscardPile(Configuration(
    ...     deck=ConfigurationDeck(contents=[
    ...         (Colors.BLUE, ConfigurationColorContents([3, 2, 1, 1])),
    ...         (Colors.RED, ConfigurationColorContents([2, 1])),
    ...     ])
    ... ))
    >>> print(discard_pile)
    No card discarded yet
    >>> print(discard_pile.array)
    [[0 0 0 0]
     [0 0 0 0]]
    >>> print(discard_pile.not_discarded)
    [[3 2 1 1]
     [2 1 0 0]]
    >>> print(discard_pile.scorable)
    [[ True  True  True  True]
     [ True  True False False]]
    >>> print(discard_pile.max_score_possible)
    6
    """

    def __init__(self, cfg: Configuration):
        self.cfg = cfg
        self.chronological = []
        self.array = np.zeros(cfg.deck_array.shape, dtype=int)
        self.not_discarded = np.copy(cfg.deck_array)
        # This formula below is valid only at the beginning because there is no
        # "holes" (zeros) in the middle of some rows.
        self.scorable = (cfg.deck_array > 0)

    def __repr__(self) -> str:
        return '<DiscardPile: %s>' % self.str_compact_chronological()

    def colored(self) -> str:
        return self.colored_multi_line_compact()

    @property
    def max_score_possible(self):
        """
        Maximum possible score, considering the discard pile.

        :return: the maximum score that is still possible.
        """
        return np.sum(self.scorable)

    def str_multi_line_compact(self) -> str:
        """
        Convert to nice string.

        :return: a representation of the discard pile. As of now, it is the
            one used for the standard method :meth:`__str__` (this behavior
            might be modified in the future).

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> print(discard_pile.str_multi_line_compact())
        B1 B3
        R4
        """
        return uncolor(self.colored_multi_line_compact())

    def colored_multi_line_compact(self) -> str:
        """
        Colored version of :meth:`str_multi_line_compact`.
        """
        if len(self.chronological) == 0:
            return 'No card discarded yet'
        lines = []
        for i, c in enumerate(self.cfg.colors):
            if np.sum(self.array[i, :]) == 0:
                continue
            words = [str(Card(c, v))
                     for j, v in enumerate(self.cfg.values)
                     for _ in range(self.array[i, j])]
            lines.append(c.color_str(' '.join(words)))
        return '\n'.join(lines)

    def str_multi_line(self) -> str:
        """
        Convert to nice string.

        :return: a representation of the discard pile.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> print(discard_pile.str_multi_line())
        B1 B3
        -
        R4
        -
        -
        """
        return uncolor(self.colored_multi_line())

    def colored_multi_line(self) -> str:
        """
        Colored version of :meth:`str_multi_line`.
        """
        lines = []
        for i, c in enumerate(self.cfg.colors):
            if np.sum(self.array[i, :]) == 0:
                lines.append(c.color_str('-'))
                continue
            words = [str(Card(c, v))
                     for j, v in enumerate(self.cfg.values)
                     for _ in range(self.array[i, j])]
            lines.append(c.color_str(' '.join(words)))
        return '\n'.join(lines)

    def str_as_array(self) -> str:
        """
        Convert to string in an array-style layout.

        :return: a representation of the discard pile.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> print(discard_pile.str_as_array())
           1 2 3 4 5
        B [1 0 1 0 0]
        G [0 0 0 0 0]
        R [0 0 0 1 0]
        W [0 0 0 0 0]
        Y [0 0 0 0 0]
        """
        return uncolor(self.colored_as_array())

    def colored_as_array(self) -> str:
        """
        Colored version of :meth:`str_as_array`.
        """
        to_join = [
            '   ' + ' '.join([str(i + 1) for i in range(self.cfg.n_values)])
        ]
        for i, c in enumerate(self.cfg.colors):
            to_join.append(
                c.color_str('%s %s' % (c.symbol, self.array[i, :]))
            )
        return '\n'.join(to_join)

    def str_compact_factorized(self) -> str:
        """
        Convert to nice string.

        :return: a representation of the discard pile.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> print(discard_pile.str_compact_factorized())
        B 1 3  R 4
        """
        return uncolor(self.colored_compact_factorized())

    def colored_compact_factorized(self) -> str:
        """
        Colored version of :meth:`str_multi_line_compact`.
        """
        if len(self.chronological) == 0:
            return 'No card discarded yet'
        lines = []
        for i, c in enumerate(self.cfg.colors):
            if np.sum(self.array[i, :]) == 0:
                continue
            words = [str(v)
                     for j, v in enumerate(self.cfg.values)
                     for _ in range(self.array[i, j])]
            lines.append(c.color_str(c.symbol + ' ' + ' '.join(words)))
        return '  '.join(lines)

    def str_compact_ordered(self) -> str:
        """
        Convert to string in a list-style layout, ordered by color and value.

        :return: a representation of the discard pile.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> print(discard_pile.str_compact_ordered())
        B1 B3 R4
        """
        return uncolor(self.colored_compact_ordered())

    def colored_compact_ordered(self) -> str:
        """
        Colored version of :meth:`str_compact_ordered`.
        """
        if not self.chronological:
            return 'No card discarded yet'
        return str_from_iterable(
            [card.colored() for card in self.list_reordered])

    def str_compact_chronological(self) -> str:
        """
        Convert to string in a list-style layout, by chronological order.

        :return: a representation of the discard pile.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> print(discard_pile.str_compact_chronological())
        B3 R4 B1
        """
        return uncolor(self.colored_compact_chronological())

    def colored_compact_chronological(self) -> str:
        """
        Colored version of :meth:`str_compact_chronological`.
        """
        if not self.chronological:
            return 'No card discarded yet'
        return str_from_iterable(
            [card.colored() for card in self.chronological])

    @property
    def list_reordered(self) -> List[Card]:
        """
        List of discarded cards, ordered by color and value.

        :return: the list of discarded cards, by lexicographic order. The order
            on the colors is the one specified in :attr:`cfg`.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('R4'))
        >>> discard_pile.receive(Card('B1'))
        >>> discard_pile.list_reordered
        [<Card: B1>, <Card: B3>, <Card: R4>]
        """
        ordered = []
        for i, c in enumerate(self.cfg.colors):
            for j, v in enumerate(self.cfg.values):
                ordered.extend([Card(c, v)] * self.array[i, j])
        return ordered

    def receive(self, card) -> None:
        """
        Receive a card.

        :param card: the card discarded.

        Update the internal variables of the discard pile.

        >>> from hanabython import Configuration
        >>> discard_pile = DiscardPile(Configuration.STANDARD)
        >>> discard_pile.receive(Card('B3'))
        >>> discard_pile.receive(Card('B2'))
        >>> discard_pile.receive(Card('B3'))
        >>> print(discard_pile)
        B2 B3 B3
        >>> print(discard_pile.not_discarded)
        [[3 1 0 2 1]
         [3 2 2 2 1]
         [3 2 2 2 1]
         [3 2 2 2 1]
         [3 2 2 2 1]]
        >>> print(discard_pile.scorable)
        [[ True  True False False False]
         [ True  True  True  True  True]
         [ True  True  True  True  True]
         [ True  True  True  True  True]
         [ True  True  True  True  True]]
        >>> print(discard_pile.max_score_possible)
        22
        """
        self.chronological.append(card)
        i = self.cfg.i_from_c(card.c)
        j = self.cfg.i_from_v(card.v)
        self.array[i, j] += 1
        self.not_discarded[i, j] -= 1
        if self.not_discarded[i, j] == 0:
            self.scorable[i, j:] = False


if __name__ == '__main__':
    my_discard_pile = DiscardPile(Configuration.W_MULTICOLOR_SHORT)
    my_discard_pile.receive(Card('R3'))
    my_discard_pile.receive(Card('R3'))
    my_discard_pile.receive(Card('M1'))
    my_discard_pile.receive(Card('B4'))
    my_discard_pile.receive(Card('B1'))
    my_discard_pile.test_str()

    print('\nAll layout styles (colored version):')
    print('Compact chronological: ')
    print(my_discard_pile.colored_compact_chronological())
    print('\nCompact ordered: ')
    print(my_discard_pile.colored_compact_ordered())
    print('\nCompact factorized: ')
    print(my_discard_pile.colored_compact_factorized())
    print('\nMulti-line compact: ')
    print(my_discard_pile.colored_multi_line_compact())
    print('\nMulti-line: ')
    print(my_discard_pile.colored_multi_line())
    print('\nAs an array: ')
    print(my_discard_pile.colored_as_array())

    import doctest
    doctest.testmod()
