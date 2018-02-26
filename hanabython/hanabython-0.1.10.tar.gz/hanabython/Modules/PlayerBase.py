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
from hanabython.Modules.Card import Card
from hanabython.Modules.StringUtils import uncolor, title
from hanabython.Modules.Configuration import Configuration
from hanabython.Modules.ConfigurationEndRule import ConfigurationEndRule
from hanabython.Modules.Board import Board
from hanabython.Modules.DiscardPile import DiscardPile
from hanabython.Modules.DrawPilePublic import DrawPilePublic
from hanabython.Modules.DrawPile import DrawPile
from hanabython.Modules.Hand import Hand
from hanabython.Modules.HandPublic import HandPublic
from hanabython.Modules.StringAnsi import StringAnsi
from hanabython.Modules.Player import Player


class PlayerBase(Player):
    """
    A player for Hanabi with basic features.

    This class is meant to serve as a mother class for most AIs and interface
    for human players. It provides all basic features, such as keeping
    track of the number of cards in the draw pile, the cards in the other
    players' hands, the clues given, etc.

    Note that all the variables are "personal" to this player: the :class:`Game`
    does not share access to its internal variables with the players.

    Note also that most methods are not supposed to work before
    :meth:`receive_init` is run at least once, which initializes all the
    variables for a new game.

    :param str name: the name of the player.

    :var list player_names: a list of strings, each with a player's name. By
        convention, the list is always rotated to that this player has
        position 0, the next player has position 1, etc.
    :var int n_players: the number of players.
    :var Configuration cfg: the configuration of the game.
    :var Board board: the board.
    :var DrawPilePublic draw_pile: the draw pile.
    :var DiscardPile discard_pile: the discard pile.
    :var int n_clues: the number of clues left.
    :var int n_misfires: the number of misfires (initially 0).
    :var int hand_size: the initial hand size.
    :var list hands: a list of Hand objects. The hand in position 0,
        corresponding to this player, is never updated because the player does
        not know what she has.
    :var list hands_public: a list of HandPublic objects. This allow the player
        to keep track, not only of her own clues, but also of the clues received
        by her partners.
    :var int remaining_turns: the number of remaining turns (once the draw pile
        is empty, in the normal rule for end of game). As long as the draw pile
        contains cards, this variable is `None`.
    :var str recent_events: things that happened "recently" (typically, since
        this player's last turn). Subclasses may typically print and/or empty
        this variable from time to time. Cf. :meth:`log`.
    :var bool dealing_is_ongoing: True only during the initial dealing of
        hands. Avoid useless verbose messages in :attr:`recent events`.
        Cf. :meth:`log`.
    :var int display_width: the width of the display on the terminal (in number
        of characters).

    >>> antoine = PlayerBase(name='Antoine')
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.player_names = None        # type: List[str]
        self.n_players = None           # type: int
        self.cfg = None                 # type: Configuration
        self.board = None               # type: Board
        self.draw_pile = None           # type: DrawPilePublic
        self.discard_pile = None        # type: DiscardPile
        self.n_clues = None             # type: int
        self.n_misfires = None          # type: int
        self.hand_size = None           # type: int
        self.hands = None               # type: List[Hand]
        self.hands_public = None        # type: List[HandPublic]
        self.remaining_turns = None     # type: int
        self.dealing_is_ongoing = None  # type: bool
        self.recent_events = None       # type: str
        self.display_width = None       # type: int

    # *** String functions ***

    def __repr__(self) -> str:
        try:
            repr_width = (self.cfg.n_values + 1) * 2 * self.cfg.n_colors - 1
        except AttributeError:
            repr_width = 60
        return (
            '<PlayerBase:\n'
            + ''.join([
                title(attr, repr_width) + '\n'
                + str(self.__getattribute__(attr)) + '\n'
                for attr in sorted(self.__dict__.keys())
            ])
            + '>'
        )

    def colored(self) -> str:
        if self.cfg is None:
            return super().colored()
        # noinspection PyListCreation
        lines = []
        lines.append(title('Recent Events', self.display_width))
        lines.append(self.recent_events)
        lines.append(title('Hands', self.display_width))
        lines.append(self.colored_hands())
        lines.append(title('Board', self.display_width))
        lines.append(self.board.colored_fixed_space())
        lines.append(title('Discard Pile', self.display_width))
        lines.append(self.discard_pile.colored_compact_factorized())
        lines.append(title('Status', self.display_width))
        draw_line = 'Draw pile: %s.' % self.draw_pile.colored()
        if (self.cfg.end_rule == ConfigurationEndRule.NORMAL
                and self.remaining_turns is not None):
            draw_line += ' %s turns remaining!' % self.remaining_turns
        lines.append(draw_line)
        lines.append(
            (StringAnsi.BLUE + '%s' + StringAnsi.RESET
             + ' clues left (out of %s). '
             + StringAnsi.RED + '%s' + StringAnsi.RESET
             + ' misfires (out of %s).')
            % (self.n_clues, self.cfg.n_clues,
               self.n_misfires, self.cfg.n_misfires)
        )
        return '\n'.join(lines)

    def colored_hands(self) -> str:
        """
        A string used to display the hands of all players.

        :return: the string (whose width is usually :attr:`display_width`,
            except maybe in the end of game when the hands are shorter).

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.demo_game()
        >>> from hanabython import uncolor
        >>> print(uncolor(antoine.colored_hands()))  \
#doctest: +NORMALIZE_WHITESPACE
        Antoine
        BGRWY 12345, BGRWY 2345 ,   BGRWY 1  ,   BGRWY 1  , BGRWY 2345
        <BLANKLINE>
        Donald X
            Y2     ,     R1     ,     R3     ,     G3     ,     Y4
        BGRWY 2345 ,   BGRWY 1  , BGRWY 2345 , BGRWY 2345 , BGRWY 2345
        <BLANKLINE>
        Uwe
            G4     ,     B4     ,     W4     ,     G5     ,     W1
        BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345
        """
        # noinspection PyListCreation
        lines = []
        lines.append(self.name)
        lines.append(self.hands_public[0].colored())
        for i, name in enumerate(self.player_names):
            if i == 0:
                continue
            lines.append('')
            lines.append(name)
            lines.append(', '.join([
                self._large_card_color(card) for card in self.hands[i]
            ]))
            lines.append(self.hands_public[i].colored())
        return '\n'.join(lines)

    # noinspection PyProtectedMember
    def _large_card(self, card: Card) -> str:
        """
        A string for a :class:`Card`, but as wide as a :attr:`CardPublic`.

        This works only once :attr:`cfg` is initialized, which is done via
        :meth:`receive_init`. Indeed, the configuration is needed to known
        the width.

        :param card: the card.

        :return: the large string.

        >>> from hanabython import Card, CardPublic
        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(cfg=Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> print('<%s>' % antoine._large_card(Card('B5')))
        <    B5     >
        >>> print('<%s>' % CardPublic(antoine.cfg))
        <BGRWY 12345>
        """
        return uncolor(self._large_card_color(card))

    # noinspection PyProtectedMember
    def _large_card_color(self, card: Card) -> str:
        """
        Colored version of :meth:`_large_card`
        """
        width = self.cfg.n_colors + self.cfg.n_values + 1
        s = str(card)
        left = (width - len(s)) // 2
        right = width - len(s) - left
        return ' ' * left + card.colored() + ' ' * right

    # *** Internal log (for the player) ***

    def log(self, o: object) -> None:
        """
        Log events for the player.

        :param o: an object. The method adds `str(o)` to the variable
            :attr:`recent_events`, except during the initial dealing of cards
            (to avoid useless messages about each card dealt). Do not forget
            the end-of-line character when relevant (it is not added
            automatically).

        This is for the player herself: it is used, in particular, in the
        subclass :class:`PlayerHumanText` to inform the player of the most
        recent events in a relatively user-friendly form.

        N.B.: this is totally different from the use of the standard package
        ``logging``, which is essentially used for debugging purposes.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.log_init()
        >>> antoine.log('Something happens.\\n')
        >>> antoine.dealing_is_ongoing = True
        >>> antoine.log('Many useless messages.\\n')
        >>> antoine.dealing_is_ongoing = False
        >>> antoine.log('Something else happens.\\n')
        >>> print(antoine.recent_events)
        Something happens.
        Something else happens.
        <BLANKLINE>
        >>> antoine.log_forget()
        >>> antoine.log('Something new happens.')
        >>> print(antoine.recent_events)
        Something new happens.
        """
        if not self.dealing_is_ongoing:
            self.recent_events += str(o)

    def log_init(self) -> None:
        """
        Initialize the log process (at the beginning of a game).

        Empties :attr:`recent_events`.
        """
        self.recent_events = ''

    def log_forget(self) -> None:
        """
        Forget old events (during the game).

        Empties :attr:`recent_events`. In this base class, this method has the
        same implementation as :meth:`log_init`, but it could be different
        in some subclasses.
        """
        self.recent_events = ''

    # *** Game start ***

    def receive_init(self, cfg: Configuration, player_names: List[str]) -> None:
        """
        Initialize all the instance variables for a new game.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> print(repr(antoine))  #doctest: +NORMALIZE_WHITESPACE
        <PlayerBase:
        ************************** board **************************
        B -         G -         R -         W -         Y -
        *************************** cfg ***************************
        Deck: normal.
        Number of clues: 8.
        Number of misfires: 3.
        Clues rule: empty clues are forbidden.
        End rule: normal.
        ******************* dealing_is_ongoing ********************
        False
        ********************** discard_pile ***********************
        No card discarded yet
        ********************** display_width **********************
        63
        ************************ draw_pile ************************
        50 cards left
        ************************ hand_size ************************
        5
        ************************** hands **************************
        [<Hand: >, <Hand: >]
        ********************** hands_public ***********************
        [<HandPublic: >, <HandPublic: >]
        ************************* n_clues *************************
        8
        *********************** n_misfires ************************
        0
        ************************ n_players ************************
        2
        ************************** name ***************************
        Antoine
        ********************** player_names ***********************
        ['Antoine', 'Donald X']
        ********************** recent_events **********************
        Configuration
        -------------
        Deck: normal.
        Number of clues: 8.
        Number of misfires: 3.
        Clues rule: empty clues are forbidden.
        End rule: normal.
        <BLANKLINE>
        ********************* remaining_turns *********************
        None
        >
        """
        self.player_names = player_names
        self.n_players = len(player_names)
        self.cfg = cfg
        self.board = Board(cfg)
        self.draw_pile = DrawPilePublic(cfg)
        self.discard_pile = DiscardPile(cfg)
        self.n_clues = cfg.n_clues
        self.n_misfires = 0
        self.hand_size = cfg.hand_size_rule.f(self.n_players)
        self.hands = [Hand() for _ in player_names]
        self.hands_public = [HandPublic(cfg) for _ in player_names]
        self.dealing_is_ongoing = False
        self.display_width = (
            self.cfg.n_colors + 3 + self.cfg.n_values) * self.hand_size - 2
        self.log_init()
        self.log('Configuration\n')
        self.log('-------------\n')
        self.log(self.cfg.colored())
        self.log('\n')

    def receive_begin_dealing(self) -> None:
        """
        The log is turned off to avoid having a message for each card dealt.
        Cf. :meth:`log`.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.receive_begin_dealing()
        >>> antoine.dealing_is_ongoing
        True
        >>> antoine.receive_end_dealing()
        >>> antoine.dealing_is_ongoing
        False
        """
        self.dealing_is_ongoing = True

    def receive_end_dealing(self) -> None:
        """
        The log is turned back on. Cf. :meth:`log` and
        :meth:`receive_begin_dealing`.
        """
        self.dealing_is_ongoing = False
        # self.log('\nInitial hands' + '\n')
        # self.log('-------------' + '\n')
        # self.log(self.colored_hands() + '\n')
        self.log('\nFirst moves' + '\n')
        self.log('-----------' + '\n')
        self.log('The game begins.\n')

    # *** Drawing cards ***

    def receive_i_draw(self) -> None:
        """
        If there are cards in the draw pile, a card is drawn. There is one
        card less in :attr:`drawpile`, and one more in this player's hand in
        :attr:`hands_public`.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for _ in range(4):
        ...     antoine.receive_i_draw()
        >>> print(antoine.draw_pile)
        46 cards left
        >>> print(antoine.hands_public[0])
        BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345

        If there are no cards in the draw pile, nothing happens.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for _ in range(50):
        ...     antoine.receive_i_draw()
        >>> len(antoine.hands_public[0])
        50
        >>> print(antoine.draw_pile)
        No card left
        >>> antoine.receive_i_draw()
        >>> len(antoine.hands_public[0])
        50
        >>> print(antoine.draw_pile)
        No card left
        """
        if self.draw_pile.n_cards == 0:
            return
        self.draw_pile.give()
        self.hands_public[0].receive()
        self.log('%s draws a card.\n' % self.name)

    def receive_partner_draws(self, i_active: int, card: Card) -> None:
        """
        If there are cards in the draw pile, a card is drawn. There is one
        card less in :attr:`drawpile`, one more in the partner's hand in
        :attr:`hands_public`, and the actual card is added in the partner's
        hand in :attr:`hands`.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for s in ['B1', 'G3', 'Y1', 'W1', 'R5']:
        ...     antoine.receive_partner_draws(i_active=1, card=Card(s))
        >>> print(antoine.draw_pile)
        45 cards left
        >>> print(antoine.hands[1])
        R5 W1 Y1 G3 B1
        >>> print(antoine.hands_public[1])
        BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345

        If there are no cards in the draw pile, nothing happens.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for _ in range(50):
        ...     antoine.receive_partner_draws(i_active=1, card=Card('B1'))
        >>> len(antoine.hands[1])
        50
        >>> len(antoine.hands_public[1])
        50
        >>> print(antoine.draw_pile)
        No card left
        >>> antoine.receive_i_draw()
        >>> len(antoine.hands[1])
        50
        >>> len(antoine.hands_public[1])
        50
        >>> print(antoine.draw_pile)
        No card left
        """
        if card is None:
            return
        self.draw_pile.give()
        self.hands[i_active].receive(card)
        self.hands_public[i_active].receive()
        self.log('%s draws %s.\n' % (
            self.player_names[i_active], card.colored()))

    # *** Manage the 4 types of actions ***

    def receive_someone_throws(
        self, i_active: int, k: int, card: Card
    ) -> None:
        """
        The card goes in the discard pile, and players regain a clue chip.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.n_clues = 3
        >>> for s in ['B1', 'G3', 'Y1', 'W1', 'R5']:
        ...     antoine.receive_partner_draws(i_active=1, card=Card(s))
        >>> print(antoine.hands[1])
        R5 W1 Y1 G3 B1
        >>> antoine.receive_someone_throws(i_active=1, k=4, card=Card('B1'))
        >>> print(antoine.hands[1])
        R5 W1 Y1 G3
        >>> print(antoine.hands_public[1])
        BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345
        >>> print(antoine.discard_pile)
        B1
        >>> antoine.n_clues
        4
        """
        self.hands_public[i_active].give(k)
        if i_active != 0:
            self.hands[i_active].give(k)
        self.discard_pile.receive(card)
        self.n_clues += 1
        self.log('%s discards %s.\n' % (
            self.player_names[i_active], card.colored()))

    def receive_someone_plays_card(
        self, i_active: int, k: int, card: Card
    ) -> None:
        """
        If the action succeeds, the card goes on the board.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for s in ['B1', 'G3', 'Y1', 'W1', 'R5']:
        ...     antoine.receive_partner_draws(i_active=1, card=Card(s))
        >>> print(antoine.hands[1])
        R5 W1 Y1 G3 B1
        >>> antoine.receive_someone_plays_card(i_active=1, k=1, card=Card('W1'))
        >>> print(antoine.hands[1])
        R5 Y1 G3 B1
        >>> print(antoine.hands_public[1])
        BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345
        >>> print(antoine.board)  #doctest: +NORMALIZE_WHITESPACE
        B -         G -         R -         W 1         Y -

        If the action fails, the card goes in the discard pile and players get
        a misfire.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for s in ['B1', 'G3', 'Y1', 'W1', 'R5']:
        ...     antoine.receive_partner_draws(i_active=1, card=Card(s))
        >>> print(antoine.hands[1])
        R5 W1 Y1 G3 B1
        >>> antoine.receive_someone_plays_card(i_active=1, k=0, card=Card('R5'))
        >>> print(antoine.hands[1])
        W1 Y1 G3 B1
        >>> print(antoine.hands_public[1])
        BGRWY 12345, BGRWY 12345, BGRWY 12345, BGRWY 12345
        >>> print(antoine.board)  #doctest: +NORMALIZE_WHITESPACE
        B -         G -         R -         W -         Y -
        >>> print(antoine.discard_pile)
        R5
        >>> antoine.n_misfires
        1
        """
        self.hands_public[i_active].give(k)
        if i_active != 0:
            self.hands[i_active].give(k)
        success = self.board.try_to_play(card)
        if success:
            self.log('%s plays %s' % (
                self.player_names[i_active], card.colored()))
            if (card.v == self.cfg.highest[card.c]
                    and self.n_clues < self.cfg.n_clues):
                self.n_clues += 1
                self.log(' and regains a clue.\n')
            else:
                self.log('.\n')
        else:
            self.discard_pile.receive(card)
            self.n_misfires += 1
            self.log('%s tries to play %s and misfires.\n' % (
                self.player_names[i_active], card.colored()))

    def receive_someone_clues(
        self, i_active: int, i_clued: int, clue: Clue, bool_list: List[bool]
    ) -> None:
        """
        We remove a clue chip, and we update the clued player's hand in
        :attr:`hands_public`.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> for s in ['B1', 'G3', 'Y1', 'W1', 'R5']:
        ...     antoine.receive_partner_draws(i_active=1, card=Card(s))
        >>> print(antoine.hands[1])
        R5 W1 Y1 G3 B1
        >>> antoine.n_clues
        8
        >>> antoine.receive_someone_clues(
        ...     i_active=0, i_clued=1, clue=Clue(1),
        ...     bool_list=[False, True, True, False, True])
        >>> print(antoine.hands_public[1])  #doctest: +NORMALIZE_WHITESPACE
        BGRWY 2345 ,   BGRWY 1  ,   BGRWY 1  , BGRWY 2345 ,   BGRWY 1
        >>> antoine.n_clues
        7
        """
        self.n_clues -= 1
        self.hands_public[i_clued].match(clue, bool_list)
        self.log(
            '%s clues %s about %s.\n'
            % (self.player_names[i_active], self.player_names[i_clued],
               clue.colored())
        )

    def receive_someone_forfeits(self, i_active: int) -> None:
        """
        We just log the event for the player.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_someone_forfeits(i_active=1)
        >>> print(antoine.recent_events)
        Donald X forfeits.
        <BLANKLINE>
        """
        self.log('%s forfeits.\n' % self.player_names[i_active])

    # *** End of game ***

    def receive_remaining_turns(self, remaining_turns: int) -> None:
        """
        We update :attr:`remaining_turns` and log the event for the player.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_remaining_turns(remaining_turns=2)
        >>> antoine.remaining_turns
        2
        >>> print(antoine.recent_events)
        2 turns remaining!
        <BLANKLINE>
        """
        self.remaining_turns = remaining_turns
        self.log('%s turns remaining!\n' % self.remaining_turns)

    def receive_lose(self, score: int) -> None:
        """
        We just log the event for the player.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_lose(score=0)
        >>> print(antoine.recent_events)
        Antoine's team loses.
        Score: 0.
        <BLANKLINE>
        """
        self.log("%s's team loses.\n" % self.name)
        self.log('Score: %s.\n' % score)

    def receive_game_exhausted(self, score: int) -> None:
        """
        We just log the event for the player.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_game_exhausted(score=23)
        >>> print(antoine.recent_events)
        Antoine's team has reached the end of the game.
        Score: 23.
        <BLANKLINE>
        """
        self.log("%s's team has reached the end of the game.\n" % self.name)
        self.log('Score: %s.\n' % score)

    def receive_win(self, score: int) -> None:
        """
        We just log the event for the player.

        >>> antoine = PlayerBase('Antoine')
        >>> antoine.receive_init(Configuration.STANDARD,
        ...                      player_names=['Antoine', 'Donald X'])
        >>> antoine.log_forget()
        >>> antoine.receive_win(score=25)
        >>> print(antoine.recent_events)
        Antoine's team wins!
        Score: 25.
        <BLANKLINE>
        """
        self.log("%s's team wins!\n" % self.name)
        self.log('Score: %s.\n' % score)

    # *** Demo ***

    def demo_game(self) -> None:
        """
        Mimic the beginning of a game.

        This method is meant to be used for tests and examples.

        >>> from hanabython import uncolor
        >>> antoine = PlayerBase('Antoine')
        >>> antoine.demo_game()
        >>> print(uncolor(antoine.recent_events))
        Configuration
        -------------
        Deck: normal.
        Number of clues: 8.
        Number of misfires: 3.
        Clues rule: empty clues are forbidden.
        End rule: normal.
        <BLANKLINE>
        First moves
        -----------
        The game begins.
        Antoine clues Donald X about 1.
        Donald X clues Antoine about 1.
        Uwe discards R3.
        Uwe draws G4.
        Antoine plays W1.
        Antoine draws a card.
        <BLANKLINE>
        """
        import random
        random.seed(0)
        cfg = Configuration.STANDARD
        draw_pile = DrawPile(cfg)
        self.receive_init(cfg=cfg, player_names=[self.name, 'Donald X', 'Uwe'])
        self.receive_begin_dealing()
        my_hand = Hand()
        for k in range(self.hand_size):
            my_hand.receive(card=draw_pile.give())
            self.receive_i_draw()
            for i in range(1, self.n_players):
                self.receive_partner_draws(i_active=i, card=draw_pile.give())
        self.receive_end_dealing()
        self.receive_someone_clues(
            i_active=0, i_clued=1, clue=Clue(1),
            bool_list=self.hands[1].match(Clue(1)))
        self.receive_someone_clues(
            i_active=1, i_clued=0, clue=Clue(1),
            bool_list=my_hand.match(Clue(1)))
        self.receive_someone_throws(i_active=2, k=4, card=self.hands[2][4])
        self.receive_partner_draws(i_active=2, card=draw_pile.give())
        self.receive_someone_plays_card(i_active=0, k=1, card=my_hand[1])
        my_hand.receive(card=draw_pile.give())
        self.receive_i_draw()


if __name__ == '__main__':
    my_antoine = PlayerBase(name='Antoine')
    my_antoine.test_str()
    my_antoine.receive_init(Configuration.STANDARD,
                            player_names=['Antoine', 'Donald X'])
    my_antoine.test_str()

    print("""
    *******************************************************
    *                                                     *
    * Pretend that the beginning of the game is played... *
    *                                                     *
    *******************************************************
    """)
    my_antoine.demo_game()
    my_antoine.test_str()

    import doctest
    doctest.testmod()
