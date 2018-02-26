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
import logging
from hanabython.Modules.PlayerBase import PlayerBase
from hanabython.Modules.Action import Action
from hanabython.Modules.ActionClue import ActionClue
from hanabython.Modules.ActionPlayCard import ActionPlayCard
from hanabython.Modules.ActionThrow import ActionThrow
from hanabython.Modules.ActionForfeit import ActionForfeit
from hanabython.Modules.Clue import Clue
from IPython.display import clear_output
from time import sleep


class PlayerHumanText(PlayerBase):
    """
    User interface for a human player in text mode (terminal or notebook).

    :param ipython: use `True` when using the player in a notebook. This
        fixes a problem between ``clear_output`` and ``input``.

    >>> antoine = PlayerHumanText('Antoine', ipython=True)
    """

    def __init__(self, name: str, ipython=False):
        super().__init__(name)
        self.ipython = ipython

    # *** General methods about actions ***

    def receive_turn_begin(self) -> None:
        """
        We pause, then we inform the player of the most recent events.
        """
        print('\n' * 40)
        if self.ipython:
            clear_output()
            sleep(0.5)  # Essential line to prevent strange behavior in Jupyter!
        input('%s is going to play (hit Enter).\n' % self.name)
        print(self.colored())

    def choose_action(self) -> Action:
        """
        The human player gets to choose an action.
        """
        category = None             # type: int
        i = None                    # type: int
        cat_dico = {'C': Action.CLUE, 'P': Action.PLAY_CARD,
                    'D': Action.THROW, 'F': Action.FORFEIT}
        while True:
            if category is None:
                cat_str = input('\nWhat action? (C = Clue, P = Play, '
                                'D = Discard, F = Forfeit)\n')
                if not cat_str:  # Nothing in the input => try again
                    continue
                cat_str = cat_str[0].capitalize()
                if cat_str in cat_dico.keys():
                    category = cat_dico[cat_str]
            elif category in {Action.PLAY_CARD, Action.THROW}:
                k_str = input('What card? (1 = leftmost, etc.)\n')
                try:
                    k = int(k_str) - 1
                except ValueError:  # Not valid => cancel
                    category = None
                    continue
                if category == Action.PLAY_CARD:
                    return ActionPlayCard(k)
                else:
                    return ActionThrow(k)
            elif category == Action.FORFEIT:
                confirm_str = input('Do you confirm forfeit? (Y/N)\n')
                if not confirm_str:  # Nothing in the input => cancel
                    category = None
                    continue
                if confirm_str[0].capitalize() == 'Y':
                    return ActionForfeit()
                else:
                    category = None  # Not confirmed ==> cancel
            elif category == Action.CLUE:
                if i is None:
                    if self.n_players == 2:
                        i = 1
                        continue
                    i_str = input('What player? (1 = next player, etc.)\n')
                    try:
                        i = int(i_str)
                    except ValueError:  # Not valid => cancel
                        category = None
                else:
                    clue_str = input('What clue? (B, G, ..., 1, 2, ...)\n')
                    try:
                        return ActionClue(i, Clue(int(clue_str)))
                    except ValueError:
                        pass
                    try:
                        clue_str = clue_str[0].capitalize()
                        clue = Clue([
                            c for c in self.cfg.colors if c.symbol == clue_str
                        ][0])
                        return ActionClue(i, clue)
                    except IndexError:
                        category = None
                        i = None
            else:
                logging.critical('This case should never happen.')

    def receive_action_legal(self) -> None:
        """
        We forget the previous events.

        >>> from hanabython import Configuration
        >>> antoine = PlayerHumanText('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.log('Donald does something.')
        >>> antoine.recent_events
        'Donald does something.'
        >>> # Here, Antoine would choose his own action. Then...
        >>> antoine.receive_action_legal()
        >>> antoine.log("Antoine's action has such and such consequences.")
        >>> antoine.recent_events
        "Antoine's action has such and such consequences."
        """
        self.log_forget()

    def receive_action_illegal(self, s: str) -> None:
        print(s)

    def receive_turn_finished(self) -> None:
        """
        We inform the player of the most recent events, i.e. the consequences
        of her actions. Then we pause (unless this string was empty).
        Finally, we forget these recent events.
        """
        print(self.recent_events)
        if self.recent_events:
            input("Your turn is over (hit Enter).\n")
        self.log_forget()

    # *** End of game ***

    def receive_lose(self, score: int) -> None:
        """
        We print and forget the recent (unfortunate) events.

        >>> from hanabython import Configuration
        >>> antoine = PlayerHumanText('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_lose(score=0)
        Antoine's team loses.
        Score: 0.
        <BLANKLINE>
        >>> antoine.recent_events
        ''
        """
        super().receive_lose(score)
        print(self.recent_events)
        self.log_forget()

    def receive_game_exhausted(self, score: int) -> None:
        """
        We print and forget the recent events.

        >>> from hanabython import Configuration
        >>> antoine = PlayerHumanText('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_game_exhausted(score=23)
        Antoine's team has reached the end of the game.
        Score: 23.
        <BLANKLINE>
        >>> antoine.recent_events
        ''
        """
        super().receive_game_exhausted(score)
        print(self.recent_events)
        self.log_forget()

    def receive_win(self, score: int) -> None:
        """
        We print and forget the recent (cheerful) events.

        >>> from hanabython import Configuration
        >>> antoine = PlayerHumanText('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_win(score=25)
        Antoine's team wins!
        Score: 25.
        <BLANKLINE>
        >>> antoine.recent_events
        ''
        """
        super().receive_win(score)
        print(self.recent_events)
        self.log_forget()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
