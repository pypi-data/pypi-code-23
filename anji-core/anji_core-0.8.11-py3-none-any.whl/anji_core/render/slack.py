import re
from typing import Tuple

from errbot.backends.base import Card, Identifier, Message

from ..types import MessageType, Reaction, RenderFeatures
from ..internal import INTERNAL_BUS_LABEL
from .base import AbstractRenderEngine

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

MD_ESCAPE_SLACK_RE = re.compile('|'.join(re.escape(c) for c in ('\\', '`', '*', '>', '#', '+')))


class SlackRenderEngine(AbstractRenderEngine):

    _reaction_map = {
        Reaction.confirm: 'white_check_mark',
        Reaction.deny: 'x',
        Reaction.okey: '+1',
        Reaction.processing: 'clock1',
        Reaction.waiting: 'clock1',
        Reaction.accepted: 'dart',
        Reaction.problem: 'izakaya_lantern',
        Reaction.processing_next: 'black_right_pointing_double_triangle_with_vertical_bar',
        Reaction.empty: 'zero',
        Reaction.blocked: 'broken_heart'
    }

    def md_escape(self, txt):
        """ Call this if you want to be sure your text won't be interpreted as markdown
        :param txt: bare text to escape.
        """
        return MD_ESCAPE_SLACK_RE.sub(lambda match: '\\' + match.group(0), txt)

    def reply(self, message, target_message, escape_markdown=True):
        if target_message:
            self.bot.send_simple_reply(target_message, message, threaded=True)
        else:
            self.send(message, escape_markdown=True)

    def send(self, message, escape_markdown=True, channel=None):
        if channel is None:
            channel = self.bot['default_channel']
        self.bot.send(
            self.bot.build_identifier(channel),
            message
        )

    def flush(self):
        text_results = []
        for custom_object in self.custom_objects:
            text_results.append(custom_object.render_markdown())
        card_data = dict(
            title=self._message_title,
            body="\n".join(text_results),
            color=MessageType.slack_color(self._message_type),
        )
        if self._in_reply_to:
            card_data['in_reply_to'] = self._in_reply_to
        else:
            card_data['to'] = self.bot.build_identifier(self.bot['default_channel'])
        self.send_card(**card_data)

    def send_card(  # pylint: disable=too-many-arguments
            self,
            body: str = '',
            to: Identifier = None,
            in_reply_to: Message = None,
            summary: str = None,
            title: str = '',
            link: str = None,
            image: str = None,
            thumbnail: str = None,
            color: str = 'green',
            fields: Tuple[Tuple[str, str], ...]=()) -> None:
        """
        Sends a card.
        A Card is a special type of preformatted message. If it matches with a backend similar concept like on
        Slack or Hipchat it will be rendered natively, otherwise it will be sent as a regular formatted message.
        Copied from original errbot logic
        :param body: main text of the card in markdown.
        :param to: the card is sent to this identifier (Room, RoomOccupant, Person...).
        :param in_reply_to: the original message this message is a reply to (optional).
        :param summary: (optional) One liner summary of the card, possibly collapsed to it.
        :param title: (optional) Title possibly linking.
        :param link: (optional) url the title link is pointing to.
        :param image: (optional) link to the main image of the card.
        :param thumbnail: (optional) link to an icon / thumbnail.
        :param color: (optional) background color or color indicator.
        :param fields: (optional) a tuple of (key, value) pairs.
        """
        if in_reply_to.extras.get(INTERNAL_BUS_LABEL, False):
            in_reply_to = None
        frm = in_reply_to.to if in_reply_to else self.bot.bot_identifier
        if to is None:
            if in_reply_to is None:
                to = self.bot.build_identifier(self.bot['default_channel'])
            else:
                to = in_reply_to.frm
        self.bot.send_card(Card(body, frm, to, in_reply_to, summary, title, link, image, thumbnail, color, fields))

    def add_reaction(self, message, reaction):
        if not message.extras.get(INTERNAL_BUS_LABEL, False):
            self.bot.add_reaction(message, self._reaction_map.get(reaction))

    def remove_reaction(self, message, reaction):
        if not message.extras.get(INTERNAL_BUS_LABEL, False):
            self.bot.remove_reaction(message, self._reaction_map.get(reaction))

    def raw_reaction(self, reaction):
        return f":{self._reaction_map.get(reaction, '')}:"

    def is_support(self, render_feature):
        return render_feature in (RenderFeatures.reaction,)
