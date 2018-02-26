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
from hanabython.Modules.Clue import Clue
from hanabython.Modules.Action import Action
from hanabython.Modules.ActionForfeit import ActionForfeit
from hanabython.Modules.Card import Card
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.Player import Player
from hanabython.Modules.StringUtils import uncolor


class PlayerPuppet(Player):
    """
    A player for Hanabi that serves only for testing purposes.

    :param speak: if True, then each time this player receives a message, she
        prints a acknowledgement.

    :var Action next_action: this variable makes it possible to control
        this player's action.

    >>> from hanabython.Modules.ActionThrow import ActionThrow
    >>> antoine = PlayerPuppet('Antoine', speak=True)
    >>> antoine.next_action = ActionThrow(k=4)
    >>> _ = antoine.choose_action()
    Antoine: Choose an action
    Antoine: action = Discard card in position 5
    """

    def __init__(self, name, speak=False):
        super().__init__(name)
        self.next_action = ActionForfeit()              # type: Action
        self.dealing_is_ongoing = False                 # type: bool
        self.speak = speak                              # type: bool

    def ack(self, o):
        if self.speak and not self.dealing_is_ongoing:
            print(uncolor('%s: %s' % (self.name, o)))

    # *** Game start ***

    def receive_init(self, cfg: Configuration, player_names: List[str]) -> None:
        self.ack('The game starts')
        self.ack('cfg = %s' % cfg)
        self.ack('player_names = %s' % player_names)

    def receive_begin_dealing(self) -> None:
        self.ack('the initial dealing of hands begins.')
        self.dealing_is_ongoing = True

    def receive_end_dealing(self) -> None:
        self.dealing_is_ongoing = False
        self.ack('The initial dealing of hands is over.')

    # *** Drawing cards ***

    def receive_i_draw(self) -> None:
        self.ack('This player tries to draw a card.')

    def receive_partner_draws(self, i_active: int, card: Card) -> None:
        self.ack('Another player tries to draw a card.')
        self.ack('i_active = %s' % i_active)
        self.ack('card = %s' % card)

    # *** General methods about actions ***

    def receive_turn_begin(self) -> None:
        self.ack('The turn of the player begins.')

    # noinspection PyMethodMayBeStatic
    def choose_action(self) -> Action:
        """
        :return: the value of :attr:`next_action`
        """
        self.ack('Choose an action')
        self.ack('action = %s' % self.next_action)
        return self.next_action

    def receive_action_legal(self) -> None:
        self.ack('The action chosen is legal.')

    def receive_action_illegal(self, s: str) -> None:
        self.ack('The action chosen is illegal.')
        self.ack(s)

    def receive_turn_finished(self) -> None:
        self.ack('The action of the player is finished.')

    # *** Manage the 4 types of actions ***

    def receive_someone_throws(self, i_active: int, k: int,
                               card: Card) -> None:
        self.ack('A player throws (discards a card willingly).')
        self.ack('i_active = %s' % i_active)
        self.ack('k = %s' % k)
        self.ack('card = %s' % card)

    def receive_someone_plays_card(
        self, i_active: int, k: int, card: Card
    ) -> None:
        self.ack('A player tries to play a card on the board.')
        self.ack('i_active = %s' % i_active)
        self.ack('k = %s' % k)
        self.ack('card = %s' % card)

    def receive_someone_clues(
        self, i_active: int, i_clued: int, clue: Clue, bool_list: List[bool]
    ) -> None:
        self.ack('A player gives a clue to another one.')
        self.ack('i_active = %s' % i_active)
        self.ack('i_clued = %s' % i_clued)
        self.ack('clue = %s' % clue)
        self.ack('bool_list = %s' % bool_list)

    def receive_someone_forfeits(self, i_active: int) -> None:
        self.ack('A player forfeits.')
        self.ack('i_active = %s' % i_active)

    # *** End of game ***

    def receive_remaining_turns(self, remaining_turns: int) -> None:
        self.ack('The number of remaining turns is now known.')
        self.ack('remaining_turns = %s' % remaining_turns)

    def receive_lose(self, score: int) -> None:
        self.ack('The game is lost.')
        self.ack('score = %s' % score)

    def receive_game_exhausted(self, score: int) -> None:
        self.ack('The game is exhausted.')
        self.ack('score = %s' % score)

    def receive_win(self, score: int) -> None:
        self.ack('The game is won.')
        self.ack('score = %s' % score)


if __name__ == '__main__':
    my_antoine = PlayerPuppet(name='Antoine')
    my_antoine.test_str()

    import doctest
    doctest.testmod()
