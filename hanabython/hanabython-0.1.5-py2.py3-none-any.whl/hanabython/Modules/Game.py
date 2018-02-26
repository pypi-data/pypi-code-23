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
from copy import copy
from typing import List
from hanabython.Modules.Card import Card
from hanabython.Modules.Clue import Clue
from hanabython.Modules.Colors import Colors
from hanabython.Modules.Colored import Colored
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.ConfigurationEmptyClueRule \
    import ConfigurationEmptyClueRule
from hanabython.Modules.ConfigurationEndRule import ConfigurationEndRule
from hanabython.Modules.PlayerHumanText import PlayerHumanText
from hanabython.Modules.PlayerPuppet import PlayerPuppet
from hanabython.Modules.Board import Board
from hanabython.Modules.DrawPile import DrawPile
from hanabython.Modules.DiscardPile import DiscardPile
from hanabython.Modules.Hand import Hand
from hanabython.Modules.Action import Action
from hanabython.Modules.ActionClue import ActionClue
from hanabython.Modules.ActionThrow import ActionThrow
from hanabython.Modules.ActionForfeit import ActionForfeit
from hanabython.Modules.ActionPlayCard import ActionPlayCard
from hanabython.Modules.Player import Player


class Game(Colored):
    """
    A game of Hanabi.

    :param cfg: the configuration.
    :param players: the list of players. They will play in this order, starting
        with the first player in this list.

    :var int n_players: the number of players.
    :var Board board: the board.
    :var DrawPile draw_pile: the draw pile.
    :var DiscardPile discard_pile: the discard pile.
    :var int n_clues: the number of clue chips that players currently have.
    :var int n_misfires: the number of misfires chips that players currently
        have.
    :var int hand_size: the initial size of the hands.
    :var list hands: a list of :class:`Hand` objects (in the same order as
        :attr:`players`).
    :var int remaining_turns: the number of remaining turns (once the draw pile
        is empty, in the normal rule for end of game). As long as the draw pile
        contains cards, this variable is `None`.
    :var bool b_lose: the game is lost.
    :var bool b_win: the game is won.
    :var int i_active: the index of the active player.
    :var Player active: the active player. It is automatically updated when
        :attr:`i_active` is updated.

    >>> game = Game(players=[PlayerHumanText('Antoine'),
    ...                      PlayerHumanText('Donald X')])
    """

    def __init__(self, players: List[Player],
                 cfg: Configuration = Configuration.STANDARD):
        logging.info('General initializations')
        # Parameters
        self.players = players
        self.cfg = cfg
        # Variables
        self.n_players = len(self.players)                  # type: int
        self.board = Board(cfg)                             # type: Board
        self.draw_pile = DrawPile(cfg)                      # type: DrawPile
        self.discard_pile = DiscardPile(cfg)                # type: DiscardPile
        self.n_clues = cfg.n_clues                          # type: int
        self.n_misfires = 0                                 # type: int
        self.hand_size = cfg.hand_size_rule.f(self.n_players)  # type: int
        self.hands = [Hand() for _ in self.players]         # type: List[Hand]
        self.remaining_turns = None                         # type: int
        self.b_lose = False                                 # type: bool
        self.b_win = False                                  # type: bool
        # Active player
        self.active = None                                  # type: Player
        self._i_active = None                               # type: int
        # Inform the players of the initialization
        for i, p in enumerate(self.players):
            p.receive_init(cfg=copy(self.cfg), player_names=(
                [self.players[j].name for j in range(i, self.n_players)]
                + [self.players[j].name for j in range(i)]
            ))

    # *** Utils ***

    @property
    def i_active(self):
        """
        Index of the active player.

        :return: this index is automatically set modulo the number of players.
        >>> game = Game(players=[PlayerHumanText('Antoine'),
        ...                      PlayerHumanText('Donald X'),
        ...                      PlayerHumanText('Uwe')])
        >>> game.i_active = 2
        >>> game.i_active += 1
        >>> print(game.i_active)
        0
        """
        return self._i_active

    @i_active.setter
    def i_active(self, value):
        """
        Updates also :attr:`active`.
        """
        self._i_active = value % self.n_players
        self.active = self.players[self._i_active]

    def rel(self, who: int, fro: int) -> int:
        """
        Relative position of a player from the point of view of another one.

        :param who: the player we talk about.
        :param fro: the player to whom we talk.

        :return: the relative position of :attr:`who` from the point of view
            of :attr:`fro`, i.e. :attr:`who` - :attr:`fro` (modulo
            :attr:`n_players`).

        >>> game = Game(players=[PlayerHumanText('Antoine'),
        ...                      PlayerHumanText('Donald X'),
        ...                      PlayerHumanText('Uwe')])
        >>> game.rel(who=1, fro=2)
        2
        """
        return (who - fro) % self.n_players

    # *** Strings ***

    def colored(self) -> str:
        return (self.cfg.colored()
                + '\nPlayers: %s.' % ', '.join([p.name for p in self.players]))

    # *** Main method: play the game ***

    #: Number of attempts that a player has to choose her action. If she
    #: provides illegal actions as many times, she is automatically considered
    #: to forfeit (and this issues a warning).
    ATTEMPTS_BEFORE_FORFEIT = 100

    def play(self) -> int:
        """
        Main method: play the game.

        Note: it is only possible to "play" once with a :class:`Game` object. If
        you want to launch a game with the same player, it is necessary
        to define a new :class:`Game`.

        :return: the final score of the game.
        """
        logging.info("Begin dealing.")
        self.i_active = -1
        self.deal()
        logging.info("The game begins.")
        while True:
            self.i_active += 1
            logging.info("Check game-exhaustion condition.")
            if self.check_game_exhausted():
                return self.game_exhausted()
            logging.info("%s's turn begins" % self.active.name)
            self.active.receive_turn_begin()
            logging.info("Ask %s for an action." % self.active.name)
            for _ in range(Game.ATTEMPTS_BEFORE_FORFEIT):
                action = self.active.choose_action()
                is_legal = self.execute_action(action)
                if is_legal:
                    break
            else:  # i.e. if all the attempts were without a legal action
                logging.warning(
                    "%s failed 100 times to choose an action. Automatic "
                    "forfeit is applied." % self.active.name)
                self.execute_action(ActionForfeit())
            logging.info("Inform %s that his/her turn is over."
                         % self.active.name)
            self.active.receive_turn_finished()
            logging.info("Check win-or-lose condition.")
            if self.b_win:
                return self.win()
            if self.b_lose:
                return self.lose()
            if self.board.score == self.discard_pile.max_score_possible:
                return self.game_exhausted()

    # *** Drawing cards ***

    def draw(self) -> None:
        """
        The active player draws a card.

        * Draw a card and put it in hand (unless the discard pile is empty).

        * If the discard pile becomes empty, launch countdown for end of game
          by setting variable :attr:`remaining_turns` to value
          :attr:`n_players` + 1. It will be decremented at the beginning of
          next player's turn (before testing the end-of-game condition).
          Cf. :meth:`check_game_exhausted`.

        >>> game = Game(players=[PlayerHumanText('Antoine'),
        ...                      PlayerHumanText('Donald X'),
        ...                      PlayerHumanText('Uwe')])
        >>> game.i_active = -1
        >>> for _ in range(50):
        ...     game.i_active += 1
        ...     game.draw()
        >>> [len(hand) for hand in game.hands]
        [17, 17, 16]
        >>> game.i_active += 1
        >>> print(game.draw())
        None
        >>> game.remaining_turns
        4
        """
        logging.debug('Draw the card from draw pile and put it in the hand '
                      '(unless the draw pile is empty).')
        card = self.draw_pile.give()
        if card is not None:
            self.hands[self.i_active].receive(card)
        logging.debug('In normal rule for end of game, check if the countdown'
                      'for end of game should be launched.')
        if (self.cfg.end_rule == ConfigurationEndRule.NORMAL
                and self.draw_pile.n_cards == 0
                and self.remaining_turns is None):
            self.remaining_turns = self.n_players + 1
        logging.debug('Inform the players that someone drew.')
        for i, p in enumerate(self.players):
            if i == self.i_active:
                p.receive_i_draw()
            else:
                p.receive_partner_draws(self.rel(self.i_active, i), copy(card))

    def deal(self) -> None:
        """
        Deal the initial hands.

        :attr:`i_active` should be -1 before dealing and will be -1 at the end
        (modulo the number of players).

        >>> game = Game(players=[PlayerHumanText('Antoine'),
        ...                      PlayerHumanText('Donald X'),
        ...                      PlayerHumanText('Uwe')])
        >>> game.i_active = -1
        >>> game.deal()
        >>> [len(hand) for hand in game.hands]
        [5, 5, 5]
        >>> game.i_active
        2
        """
        logging.debug('Inform the players that dealing begins.')
        for p in self.players:
            p.receive_begin_dealing()
        logging.debug('Deal cards.')
        for _ in range(self.n_players * self.hand_size):
            self.i_active += 1
            self.draw()
        logging.debug('Inform the players that dealing is over.')
        for p in self.players:
            p.receive_end_dealing()

    # *** Manage the 4 types of actions ***

    def execute_action(self, action: Action) -> bool:
        """
        Execute the action (by the active player).

        :param action: the action.

        :return: True iff the action is legal. If not, it will be necessary
            to choose another action.

        This method dispatches to the auxiliary methods :meth:`execute_clue`,
        :meth:`execute_forfeit`, :meth:`execute_play_card` and
        :meth:`execute_throw`. Each of these methods has the responsability to:

        * Check if the action is legal,

        * Inform the active player whether it is the case or not,

        * Perform the action,

        * Update the relevant variables, in particular :attr:`b_lose` and
          :attr:`b_win`.

        * Inform all players of the result of the action,

        * Make the active player draw a new card if necessary,

        * Return the boolean stating whether the action is legal.
        """
        if isinstance(action, ActionForfeit):
            return self.execute_forfeit()
        if isinstance(action, ActionThrow):
            return self.execute_throw(k=action.k)
        if isinstance(action, ActionPlayCard):
            return self.execute_play_card(k=action.k)
        if isinstance(action, ActionClue):
            return self.execute_clue(
                i_clued=(self.i_active + action.i) % self.n_players,
                clue=action.clue)

    def execute_forfeit(self) -> bool:
        """
        Execute the action: forfeit.

        :return: True (meaning that this action is always legal).

        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.players[1].speak = True
        >>> game.i_active = 1
        >>> is_legal = game.execute_forfeit()
        Donald X: The action chosen is legal.
        Donald X: A player forfeits.
        Donald X: i_active = 0
        >>> is_legal
        True
        >>> game.b_lose
        True
        >>> game.i_active = 2
        >>> is_legal = game.execute_forfeit()
        Donald X: A player forfeits.
        Donald X: i_active = 1
        >>> is_legal
        True
        >>> game.b_lose
        True
        """
        logging.debug('Check legality: forfeit is always legal.')
        logging.debug('Inform the active player that it is legal.')
        self.active.receive_action_legal()
        logging.debug('Perform the action.')
        self.b_lose = True
        logging.debug('Inform all players of the result of the action.')
        for i, p in enumerate(self.players):
            p.receive_someone_forfeits(self.rel(self.i_active, i))
        return True

    def execute_throw(self, k: int) -> bool:
        """
        Execute the action: throw (= discard willingly).

        :param k: the index of the card in the active player's hand.

        :return: True iff the action is legal, i.e. except if players have
            all the clue chips.

        >>> import random
        >>> random.seed(0)
        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.players[1].speak = True
        >>> game.i_active = 1
        >>> game.draw()
        Donald X: This player tries to draw a card.
        >>> is_legal = game.execute_throw(0)
        Donald X: The action chosen is illegal.
        Donald X: You cannot discard because you have all the clue chips.
        >>> is_legal
        False
        >>> game.n_clues = 3
        >>> game.i_active = 2
        >>> game.draw()
        Donald X: Another player tries to draw a card.
        Donald X: i_active = 1
        Donald X: card = Y4
        >>> is_legal = game.execute_throw(0)
        Donald X: A player throws (discards a card willingly).
        Donald X: i_active = 1
        Donald X: k = 0
        Donald X: card = Y4
        Donald X: Another player tries to draw a card.
        Donald X: i_active = 1
        Donald X: card = R3
        >>> is_legal
        True
        >>> game.n_clues
        4
        >>> print(game.discard_pile)
        Y4
        >>> print(game.hands[2])
        R3
        """
        logging.debug('Discard: Check legality and inform the active player.')
        if self.n_clues == self.cfg.n_clues:
            self.active.receive_action_illegal(
                'You cannot discard because you have all the clue chips.')
            return False
        self.active.receive_action_legal()
        logging.debug('Perform the throw action.')
        card = self.hands[self.i_active].give(k)
        self.discard_pile.receive(card)
        self.n_clues += 1
        logging.debug('Inform all players of the result of the action.')
        for i, p in enumerate(self.players):
            p.receive_someone_throws(self.rel(self.i_active, i), k, card)
        logging.debug('Draw a card')
        self.draw()
        return True

    def execute_play_card(self, k: int) -> bool:
        """
        Execute the action: try to play a card.

        :param k: the index of the card in the active player's hand.

        :return: True (meaning that this action is always legal).

        The action can fail, in the sense that it leads to a misfire, but it
        is legal anyway. If it leads to the last misfire, then the players lose:

        >>> import random
        >>> random.seed(0)
        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.i_active = -1
        >>> game.deal()
        >>> game.i_active = 2
        >>> game.n_misfires = 2
        >>> print(game.hands[2])
        B4 W4 G5 W1 R3
        >>> game.players[1].speak = True
        >>> is_legal = game.execute_play_card(2)
        Donald X: A player tries to play a card on the board.
        Donald X: i_active = 1
        Donald X: k = 2
        Donald X: card = G5
        >>> is_legal
        True
        >>> print(game.board)  #doctest: +NORMALIZE_WHITESPACE
        B -         G -         R -         W -         Y -
        >>> print(game.discard_pile)
        G5
        >>> game.n_misfires
        3
        >>> game.b_lose
        True

        If the highest card in a color is played, then the players gain a clue:

        >>> import random
        >>> random.seed(0)
        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.i_active = -1
        >>> game.deal()
        >>> for s in ['G1', 'G2', 'G3', 'G4']:
        ...     _ = game.board.try_to_play(card=Card(s))
        >>> game.n_clues = 3
        >>> game.i_active = 2
        >>> print(game.hands[2])
        B4 W4 G5 W1 R3
        >>> game.players[1].speak = True
        >>> is_legal = game.execute_play_card(2)
        Donald X: A player tries to play a card on the board.
        Donald X: i_active = 1
        Donald X: k = 2
        Donald X: card = G5
        Donald X: Another player tries to draw a card.
        Donald X: i_active = 1
        Donald X: card = G4
        >>> is_legal
        True
        >>> print(game.board)  #doctest: +NORMALIZE_WHITESPACE
        B -         G 1 2 3 4 5 R -         W -         Y -
        >>> game.n_clues
        4

        But players cannot gain a clue if they already have the maximum
        number of clues:

        >>> import random
        >>> random.seed(0)
        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.i_active = -1
        >>> game.deal()
        >>> for s in ['G1', 'G2', 'G3', 'G4']:
        ...     _ = game.board.try_to_play(card=Card(s))
        >>> game.n_clues
        8
        >>> game.i_active = 2
        >>> print(game.hands[2])
        B4 W4 G5 W1 R3
        >>> game.players[1].speak = True
        >>> is_legal = game.execute_play_card(2)
        Donald X: A player tries to play a card on the board.
        Donald X: i_active = 1
        Donald X: k = 2
        Donald X: card = G5
        Donald X: Another player tries to draw a card.
        Donald X: i_active = 1
        Donald X: card = G4
        >>> is_legal
        True
        >>> print(game.board)  #doctest: +NORMALIZE_WHITESPACE
        B -         G 1 2 3 4 5 R -         W -         Y -
        >>> game.n_clues
        8

        If the card completes the board, then the players win the game.

        >>> import random
        >>> random.seed(0)
        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.i_active = -1
        >>> game.deal()
        >>> for c in ['B', 'R', 'W', 'Y']:
        ...     for v in range(1, 6):
        ...         _ = game.board.try_to_play(card=Card(c + str(v)))
        >>> for s in ['G1', 'G2', 'G3', 'G4']:
        ...     _ = game.board.try_to_play(card=Card(s))
        >>> game.i_active = 2
        >>> print(game.hands[2])
        B4 W4 G5 W1 R3
        >>> game.players[1].speak = True
        >>> _ = game.execute_play_card(2)
        Donald X: A player tries to play a card on the board.
        Donald X: i_active = 1
        Donald X: k = 2
        Donald X: card = G5
        >>> print(game.board)  #doctest: +NORMALIZE_WHITESPACE
        B 1 2 3 4 5 G 1 2 3 4 5 R 1 2 3 4 5 W 1 2 3 4 5 Y 1 2 3 4 5
        >>> game.b_win
        True
        """
        logging.debug('Check legality: play a card is always legal.')
        logging.debug('Inform the active player that it is legal.')
        self.active.receive_action_legal()
        logging.debug('Perform the "play a card" action.')
        card = self.hands[self.i_active].give(k)
        success = self.board.try_to_play(card)
        if success:
            if card.v == self.cfg.highest[card.c]:
                self.n_clues = min(self.n_clues + 1, self.cfg.n_clues)
            if self.board.score == self.cfg.max_score:
                self.b_win = True
        else:
            self.discard_pile.receive(card)
            self.n_misfires += 1
            if self.n_misfires == self.cfg.n_misfires:
                self.b_lose = True
        logging.debug('Inform all players of the result of the action.')
        for i, p in enumerate(self.players):
            p.receive_someone_plays_card(
                self.rel(self.i_active, i), k, copy(card))
        if not self.b_lose and not self.b_win:
            logging.debug('Draw a card')
            self.draw()
        return True

    def execute_clue(self, i_clued: int, clue: Clue) -> bool:
        """
        Execute the action: give a clue.

        :param i_clued: the index of the player who receives the clue.
        :param clue: the clue.

        :return: True iff the action is legal.

        >>> import random
        >>> random.seed(0)
        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')],
        ...             cfg=Configuration.W_MULTICOLOR)
        >>> game.i_active = -1
        >>> game.deal()
        >>> print(game.hands[2])
        G2 W1 W1 B1 Y4
        >>> game.players[1].speak = True
        >>> game.i_active = 1
        >>> game.n_clues = 0
        >>> game.execute_clue(2, Clue(1))
        Donald X: The action chosen is illegal.
        Donald X: You cannot give a clue because you have do not have any clue \
chip.
        False
        >>> game.n_clues = 3
        >>> game.execute_clue(1, Clue(1))
        Donald X: The action chosen is illegal.
        Donald X: You cannot give a clue to yourself.
        False
        >>> game.execute_clue(2, Clue(6))
        Donald X: The action chosen is illegal.
        Donald X: This value does not exist: 6.
        False
        >>> game.execute_clue(2, Clue(Colors.COLORLESS))
        Donald X: The action chosen is illegal.
        Donald X: This color is not in the deck: C.
        False
        >>> game.execute_clue(2, Clue(Colors.MULTICOLOR))
        Donald X: The action chosen is illegal.
        Donald X: You cannot clue this color: M.
        False
        >>> game.execute_clue(2, Clue(3))
        Donald X: The action chosen is illegal.
        Donald X: You cannot give this clue because it does not correspond to \
any card.
        False
        >>> game.execute_clue(2, Clue(1))
        Donald X: The action chosen is legal.
        Donald X: A player gives a clue to another one.
        Donald X: i_active = 0
        Donald X: i_clued = 1
        Donald X: clue = 1
        Donald X: bool_list = [False, True, True, True, False]
        True
        >>> game.n_clues
        2
        """
        logging.debug('Check legality and inform the active player.')
        if self.n_clues == 0:
            self.active.receive_action_illegal(
                'You cannot give a clue because you have do not have any clue '
                'chip.')
            return False
        if i_clued == self.i_active:
            self.active.receive_action_illegal(
                'You cannot give a clue to yourself.')
            return False
        if (clue.category == Clue.VALUE
                and clue.x not in self.cfg.values):
            self.active.receive_action_illegal(
                'This value does not exist: %s.' % clue.x)
            return False
        if clue.category == Clue.COLOR and clue.x not in self.cfg.colors:
            self.active.receive_action_illegal(
                'This color is not in the deck: %s.' % clue.x)
            return False
        if clue.category == Clue.COLOR and not clue.x.is_cluable:
            self.active.receive_action_illegal(
                'You cannot clue this color: %s.' % clue.x.colored())
            return False
        bool_list = self.hands[i_clued].match(clue)
        if self.cfg.empty_clue_rule == ConfigurationEmptyClueRule.FORBIDDEN:
            if not any(bool_list):
                self.active.receive_action_illegal(
                    'You cannot give this clue because it does not correspond '
                    'to any card.')
                return False
        logging.debug('Inform the active player that the action is legal.')
        self.active.receive_action_legal()
        logging.debug('Perform the clue action.')
        self.n_clues -= 1
        logging.debug('Inform all players of the result of the action.')
        for i, p in enumerate(self.players):
            p.receive_someone_clues(
                self.rel(self.i_active, i), self.rel(i_clued, i), copy(clue),
                copy(bool_list))
        return True

    # *** End of game ***

    def check_game_exhausted(self) -> bool:
        """
        Check if the game is exhausted.

        Typically, the game end by exhaustion a bit after the deck ran out of
        cards (the exact moment depends on the end-of-game rule that is used).

        This method is called at the beginning of each player's turn.

        We do not check here whether the current score is equal to the maximum
        score still possible (considering what is discarded), which would also
        end the game. This verification is done in :meth:`play`.

        :return: True iff the game must end.

        If the normal end-of-game rule is used, and :attr:`remaining_turns`
        is an integer: it is updated, then the end-of-game condition is
        checked.

        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.players[1].speak = True
        >>> game.remaining_turns = 1
        >>> # Here, previous player would play her turn.. Then...
        >>> game.check_game_exhausted()
        Donald X: The number of remaining turns is now known.
        Donald X: remaining_turns = 0
        True
        >>> print(game.remaining_turns)
        0

        If the normal end-of-game rule is used, and :attr:`remaining_turns`
        is `None`: it is not updated (the final countdown has not started).

        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.players[1].speak = True
        >>> game.check_game_exhausted()
        False
        >>> print(game.remaining_turns)
        None

        If "Crowning piece" rule is used: if the active player has no card in
        hand, the game is over.

        >>> game = Game(
        ...     players=[PlayerPuppet('Antoine'),
        ...              PlayerPuppet('Donald X'),
        ...              PlayerPuppet('Uwe')],
        ...     cfg=Configuration(end_rule=ConfigurationEndRule.CROWNING_PIECE)
        ... )
        >>> game.players[1].speak = True
        >>> game.i_active = 1
        >>> game.check_game_exhausted()
        True
        >>> game.hands[1].receive(Card('B1'))
        >>> game.check_game_exhausted()
        False
        """
        if self.cfg.end_rule == ConfigurationEndRule.NORMAL:
            if self.remaining_turns is not None:
                self.remaining_turns -= 1
                for p in self.players:
                    p.receive_remaining_turns(self.remaining_turns)
                if self.remaining_turns == 0:
                    return True
        elif self.cfg.end_rule == ConfigurationEndRule.CROWNING_PIECE:
            if len(self.hands[self.i_active]) == 0:
                return True
        return False

    def lose(self) -> int:
        """
        Lose the game (forfeit or too many misfires).

        Inform the players.

        :return: the final score, i.e. 0.

        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> game.players[1].speak = True
        >>> score = game.lose()
        Donald X: The game is lost.
        Donald X: score = 0
        >>> score
        0
        """
        for i, p in enumerate(self.players):
            p.receive_lose(score=0)
        return 0

    def game_exhausted(self) -> int:
        """
        The game is exhausted.

        Inform the players. The game is over and is neither really lost
        (misfires, forfeit) nor a total victory (maximal score). Typically,
        this happens a bit after the deck ran out of cards (it depends on the
        end-of-game rule that is used).

        :return: the final score.

        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> _ = game.board.try_to_play(Card('B1'))
        >>> game.players[1].speak = True
        >>> score = game.game_exhausted()
        Donald X: The game is exhausted.
        Donald X: score = 1
        >>> score
        1
        """
        for i, p in enumerate(self.players):
            p.receive_game_exhausted(score=self.board.score)
        return self.board.score

    def win(self) -> int:
        """
        Win the game (maximum score).

        Inform the players.

        :return: the final score.

        >>> game = Game(players=[PlayerPuppet('Antoine'),
        ...                      PlayerPuppet('Donald X'),
        ...                      PlayerPuppet('Uwe')])
        >>> for c in ['B', 'G', 'R', 'W', 'Y']:
        ...     for v in range(1, 6):
        ...         _ = game.board.try_to_play(card=Card(c + str(v)))
        >>> game.players[1].speak = True
        >>> score = game.win()
        Donald X: The game is won.
        Donald X: score = 25
        >>> score
        25
        """
        for i, p in enumerate(self.players):
            p.receive_win(score=self.board.score)
        return self.board.score


if __name__ == '__main__':

    log_file = 'Game.log'
    open(log_file, 'w').close()  # Flush the contents of the file
    logging.basicConfig(
        filename=log_file,
        format='%(levelname)s - %(module)s - %(message)s',
        level=logging.DEBUG
    )

    # from hanabython.Modules.ConfigurationDeck import ConfigurationDeck
    # from hanabython.Modules.ConfigurationColorContents \
    #     import ConfigurationColorContents
    # cfg_test = Configuration(deck=ConfigurationDeck(contents=[
    #     (Colors.BLUE, ConfigurationColorContents([3, 2, 2])),
    #     (Colors.RED, ConfigurationColorContents([3, 2, 2])),
    # ]), end_rule=ConfigurationEndRule.CROWNING_PIECE)

    fanfan = PlayerHumanText(name='Fanfan')
    emilie = PlayerHumanText(name='Emilie')
    pek = PlayerHumanText(name='PEK')
    game = Game([fanfan, emilie])
    # game.test_str()
    game.play()

    # import doctest
    # doctest.testmod()
