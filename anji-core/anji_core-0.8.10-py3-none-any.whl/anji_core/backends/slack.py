import logging
import json

from errbot.backends.base import Card, RoomOccupant
from errbot.backends.slack import SlackBackend, SlackAPIResponseError, SlackPerson, COLORS
from slackclient import SlackClient

from anji_core.backend import AnjiBackendMixin
from anji_core.internal import INTERNAL_BUS_LABEL

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

log = logging.getLogger('anji.backend.slack')


class AnjiSlackBackend(AnjiBackendMixin, SlackBackend):

    def serve_once_required(self) -> None:
        self.sc = SlackClient(self.token)
        log.info("Verifying authentication token")
        self.auth = self.api_call("auth.test", raise_errors=False)
        if not self.auth['ok']:
            raise SlackAPIResponseError(error="Couldn't authenticate with Slack. Server said: %s" % self.auth['error'])
        log.debug("Token accepted")
        self.bot_identifier = SlackPerson(self.sc, self.auth["user_id"])
        if self.sc.rtm_connect():
            log.info("Connected")
            self.sc.server.websocket.sock.setblocking(True)
            self.reset_reconnection_count()
            self.update_alternate_prefixes()
        else:
            raise Exception('Connection failed, invalid token ?')

    def build_message_identifier(self, txtrep, message_extras):
        identifier = self.build_identifier(txtrep)
        if hasattr(identifier, '_channelid') and not message_extras.get(INTERNAL_BUS_LABEL, False):
            identifier._channelid = message_extras['slack_event']['channel']
        return identifier

    def send_card(self, card: Card):
        """
        Copied from original method to add thread_ts support from in_reply_to
        """
        if isinstance(card.to, RoomOccupant):
            card.to = card.to.room
        to_humanreadable, to_channel_id = self._prepare_message(card)
        attachment = {}
        if card.summary:
            attachment['pretext'] = card.summary
        if card.title:
            attachment['title'] = card.title
        if card.link:
            attachment['title_link'] = card.link
        if card.image:
            attachment['image_url'] = card.image
        if card.thumbnail:
            attachment['thumb_url'] = card.thumbnail
        attachment['text'] = card.body
        attachment["mrkdwn_in"] = ["text", "pretext"]

        if card.color:
            attachment['color'] = COLORS[card.color] if card.color in COLORS else card.color

        if card.fields:
            attachment['fields'] = [{'title': key, 'value': value, 'short': True} for key, value in card.fields]

        data = {
            'text': ' ',
            'channel': to_channel_id,
            'attachments': json.dumps([attachment]),
            'link_names': '1',
            'as_user': 'true',
            "mrkdwn": True
        }
        # Add thread_ts processing from parent object
        if card.parent:
            if card.parent.extras.get('thread_ts'):
                data['thread_ts'] = card.parent.extras['thread_ts']
            else:
                data['thread_ts'] = self._ts_for_message(card.parent)
        try:
            log.debug('Sending data:\n%s', data)
            self.api_call('chat.postMessage', data=data)
        except Exception:  # pylint: disable=broad-except
            log.exception("An exception occurred while trying to send a card to %s.[%s]", to_humanreadable, card)
