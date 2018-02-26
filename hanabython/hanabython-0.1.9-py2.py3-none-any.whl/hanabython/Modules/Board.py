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
import numpy as np
from hanabython.Modules.Colored import Colored
from hanabython.Modules.StringUtils import uncolor
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.Color import Color
from hanabython.Modules.Card import Card


class Board(Colored):
    """
    The board (cards successfully played) in a game of Hanabi.

    :param cfg: the configuration of the game.

    :var np.array altitude: indicates the highest card played in each color.
        E.g. with color ``c`` of index ``i``, ``altitude[i]`` is the value
        of the highest card played in color ``c``. The correspondence between
        colors and indexes is the one provided by :attr:`cfg`.

    >>> from hanabython import Configuration
    >>> board = Board(Configuration.STANDARD)
    >>> print(board.altitude)
    [0 0 0 0 0]
    """

    def __init__(self, cfg: Configuration):
        self.cfg = cfg
        self.altitude = np.zeros(self.cfg.n_colors, dtype=int)  # type: np.array

    def __repr__(self) -> str:
        return '<Board: %s>' % self.str_compact()

    def colored(self) -> str:
        return self.colored_fixed_space()

    def str_compact(self) -> str:
        """
        Convert to string in "compact" layout.

        :return: a representation of the board.

        >>> from hanabython import Configuration
        >>> board = Board(Configuration.STANDARD)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board.str_compact())
        G1 G2 Y1 Y2 Y3 Y4 Y5
        """
        return uncolor(self.colored_compact())

    def colored_compact(self) -> str:
        """
        Colored version of :meth:`str_compact`.
        """
        if self.score == 0:
            return 'No card on the board yet'
        return ' '.join([
            c.color_str(self._str_one_color(i, c))
            for i, c in enumerate(self.cfg.colors)
            if self.altitude[i] > 0
        ])

    def str_fixed_space(self) -> str:
        """
        Convert to string in "fixed-space" layout.

        :return: a representation of the board.

        >>> from hanabython import Configuration
        >>> board = Board(Configuration.STANDARD)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board.str_fixed_space())
        B -         G 1 2       R -         W -         Y 1 2 3 4 5
        """
        return uncolor(self.colored_fixed_space())

    def colored_fixed_space(self) -> str:
        """
        Colored version of :meth:`str_fixed_space`.
        """
        length = 1 + 2 * self.cfg.n_values
        return ' '.join([
            c.color_str(self._str_one_color_factorized(i, c).ljust(length))
            for i, c in enumerate(self.cfg.colors)
        ])

    def str_multi_line(self) -> str:
        """
        Convert to string in "multi-line" layout.

        :return: a representation of the board.

        >>> from hanabython import Configuration
        >>> board = Board(Configuration.STANDARD)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board.str_multi_line())
        -
        G1 G2
        -
        -
        Y1 Y2 Y3 Y4 Y5
        """
        return uncolor(self.colored_multi_line())

    def colored_multi_line(self) -> str:
        """
        Colored version of :meth:`str_multi_line`.
        """
        return '\n'.join([
            c.color_str(self._str_one_color(i, c))
            for i, c in enumerate(self.cfg.colors)
        ])

    def str_multi_line_compact(self) -> str:
        """
        Convert to string in "compact multi-line" layout.

        :return: a representation of the board.

        >>> from hanabython import Configuration
        >>> board = Board(Configuration.STANDARD)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board.str_multi_line_compact())
        G1 G2
        Y1 Y2 Y3 Y4 Y5
        """
        return uncolor(self.colored_multi_line_compact())

    def colored_multi_line_compact(self) -> str:
        """
        Colored version of :meth:`str_multi_line_compact`.
        """
        if self.score == 0:
            return 'No card on the board yet'
        return '\n'.join([
            c.color_str(self._str_one_color(i, c))
            for i, c in enumerate(self.cfg.colors)
            if self.altitude[i] > 0
        ])

    # noinspection PyProtectedMember
    def _str_one_color(self, i: int, c: Color) -> str:
        """
        Convert one color to string.

        :param i: index of the color.
        :param c: the color.

        :return: a representation of the cards played in this color.

        >>> from hanabython import Configuration
        >>> cfg = Configuration.STANDARD
        >>> board = Board(cfg)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board._str_one_color(i=4, c=cfg.colors[4]))
        Y1 Y2 Y3 Y4 Y5
        """
        if self.altitude[i] == 0:
            return '-'
        return ' '.join([
            str(Card(c, j)) for j in range(1, self.altitude[i] + 1)
        ])

    # noinspection PyProtectedMember
    def _str_one_color_factorized(self, i: int, c: Color) -> str:
        """
        Same as :meth:`_str_one_color`, but with the color symbol only once.

        :param i: index of the color.
        :param c: the color.

        :return: a representation of the cards played in this color.

        >>> from hanabython import Configuration
        >>> cfg = Configuration.STANDARD
        >>> board = Board(cfg)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board._str_one_color_factorized(i=4, c=cfg.colors[4]))
        Y 1 2 3 4 5
        """
        if self.altitude[i] == 0:
            return c.symbol + ' -'
        return c.symbol + ' ' + ' '.join([
            str(j) for j in range(1, self.altitude[i] + 1)
        ])

    def try_to_play(self, card: Card) -> bool:
        """
        Try to play a card on the board.

        :param card: the card.

        :return: True if the card is successfully played on the board, False
            otherwise (i.e. if it leads to a misfire).

        >>> from hanabython import Configuration, Card
        >>> board = Board(Configuration.STANDARD)
        >>> for s in ['B1', 'B2', 'Y1', 'Y3', 'B1']:
        ...     board.try_to_play(Card(s))
        True
        True
        True
        False
        False
        >>> print(board.str_compact())
        B1 B2 Y1
        """
        i_c = self.cfg.i_from_c(card.c)
        if card.v == self.altitude[i_c] + 1:
            self.altitude[i_c] += 1
            return True
        else:
            return False

    @property
    def score(self) -> int:
        """
        The current score.

        :return: the sum of the altitudes reached in all colors.

        >>> from hanabython import Configuration
        >>> cfg = Configuration.STANDARD
        >>> board = Board(cfg)
        >>> for s in ['G1', 'G2', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5']:
        ...     _ = board.try_to_play(Card(s))
        >>> print(board.score)
        7
        """
        return int(np.sum(self.altitude))


if __name__ == '__main__':
    my_board = Board(Configuration.W_MULTICOLOR_SHORT)
    for s in ['B1', 'B2', 'M1', 'M3', 'B1']:
        print('Try to play %s: ' % s, my_board.try_to_play(Card(s)))
    print()
    my_board.test_str()

    print('\nAll layout styles (colored version):')
    print('Compact: ')
    print(my_board.colored_compact())
    print('\nFixed space: ')
    print(my_board.colored_fixed_space())
    print('\nMulti-line compact: ')
    print(my_board.colored_multi_line_compact())
    print('\nMulti-line: ')
    print(my_board.colored_multi_line())

    import doctest
    doctest.testmod()
