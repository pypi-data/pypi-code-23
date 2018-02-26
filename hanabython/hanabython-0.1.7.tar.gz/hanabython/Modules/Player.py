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
from hanabython.Modules.Card import Card
from hanabython.Modules.Colored import Colored
from hanabython.Modules.Configuration import Configuration


class Player(Colored):
    """
    A player for Hanabi.

    :param name: the name of the player.

    To define a subclass, the only real requirement is to implement the function
    :meth:`choose_action`.

    >>> antoine = Player('Antoine')
    >>> print(antoine)
    Antoine
    """

    def __init__(self, name: str):
        self.name = name

    def colored(self) -> str:
        return self.name

    # *** Game start ***

    def receive_init(self, cfg: Configuration, player_names: List[str]) -> None:
        """
        Receive a message: the game starts.

        :param cfg: the configuration of the game.
        :param player_names: the names of the players, rotated so that this
            player corresponds to index 0.
        """
        pass

    def receive_begin_dealing(self) -> None:
        """
        Receive a message: the initial dealing of hands begins.
        """
        pass

    def receive_end_dealing(self) -> None:
        """
        Receive a message: the initial dealing of hands is over.

        The hands themselves are not communicated in this message. Drawing
        cards, including for the initial hands, is always handled by
        :meth:`receive_i_draw` or :meth:`receive_partner_draws`.
        """
        pass

    # *** Drawing cards ***

    def receive_i_draw(self) -> None:
        """
        Receive a message: this player tries to draw a card.

        A card is actually drawn only if the draw pile is not empty.
        """
        pass

    def receive_partner_draws(self, i_active: int, card: Card) -> None:
        """
        Receive a message: another player tries to draw a card.

        A card is actually drawn only if the draw pile is not empty.

        :param i_active: the position of the player who draws (relatively
            to this player).
        :param card: the card drawn.
        """
        pass

    # *** General methods about actions ***

    def receive_turn_begin(self) -> None:
        """
        Receive a message: the turn of the player begins.
        """
        pass

    # noinspection PyMethodMayBeStatic
    def choose_action(self) -> Action:
        """
        Choose an action.

        :return: the action chosen by the player.
        """
        pass

    def receive_action_legal(self) -> None:
        """
        Receive a message: the action chosen is legal.
        """
        pass

    def receive_action_illegal(self, s: str) -> None:
        """
        Receive a message: the action chosen is illegal.

        :param s: a message explaining why the action is illegal.
        """
        pass

    def receive_turn_finished(self) -> None:
        """
        Receive a message: the turn of the player is finished.
        """
        pass

    # *** Manage the 4 types of actions ***

    def receive_someone_throws(self, i_active: int, k: int,
                               card: Card) -> None:
        """
        Receive a message: a player throws (discards a card willingly).

        It is not necessary to check whether this action is legal: the
        :attr:`Game` will only send this message when it is the case.

        :param i_active: the position of the player who throws (relatively
            to this player).
        :param k: position of the card in the hand.
        :param card: the card thrown.
        """
        pass

    def receive_someone_plays_card(
        self, i_active: int, k: int, card: Card
    ) -> None:
        """
        Receive a message: a player tries to play a card on the board.

        This can be a success or a misfire.

        :param i_active: the position of the player who plays the card
            (relatively to this player).
        :param k: position of the card in the hand.
        :param card: the card played.
        """
        pass

    def receive_someone_clues(
        self, i_active: int, i_clued: int, clue: Clue, bool_list: List[bool]
    ) -> None:
        """
        Receive a message: a player gives a clue to another one.

        It is not necessary to check whether this action is legal: the
        :attr:`Game` will only send this message when it is the case.

        :param i_active: the position of the player who gives the clue
            (relatively to this player).
        :param i_clued: the position of the player who receives the clue
            (relatively to this player).
        :param clue: the clue.
        :param bool_list: a list of boolean that indicates what cards
            match the clue given.
        """
        pass

    def receive_someone_forfeits(self, i_active: int) -> None:
        """
        Receive a message: a player forfeits.

        :param i_active: the position of the player who forfeits
            (relatively to this player).
        """
        pass

    # *** End of game ***

    def receive_remaining_turns(self, remaining_turns: int) -> None:
        """
        Receive a message: the number of remaining turns is now known.

        This happens with the normal rule for end of game: as soon as the
        discard pile is empty, we know how many turns are left. N.B.:
        the word  "turn" means that one player gets to play (not all of them).

        :param remaining_turns: the number of turns left.
        """
        pass

    def receive_lose(self, score: int) -> None:
        """
        Receive a message: the game is lost (misfires or forfeit).

        :param score: the final score (0 in that case).
        """
        pass

    def receive_game_exhausted(self, score: int) -> None:
        """
        Receive a message: the game is over and is neither really lost
        (misfires, forfeit) nor a total victory (maximal score). Typically,
        this happens a bit after the deck ran out of cards (it depends on the
        end-of-game rule that is used).

        :param score: the final score.
        """
        pass

    def receive_win(self, score: int) -> None:
        """
        Receive a message: the game is won (total victory).

        :param score: the final score.
        """
        pass


if __name__ == '__main__':
    my_antoine = Player(name='Antoine')
    my_antoine.test_str()

    import doctest
    doctest.testmod()
