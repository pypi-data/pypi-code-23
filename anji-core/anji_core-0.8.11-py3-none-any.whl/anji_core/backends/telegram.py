import logging

import telegram
from errbot.backends.telegram_messenger import TelegramBackend, TelegramPerson
from errbot.core import ErrBot

from anji_core.backend import AnjiBackendMixin

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

log = logging.getLogger('errbot.backends.telegram')


class AnjiTelegramBackend(AnjiBackendMixin, TelegramBackend):

    def send_message(self, mess):  # pylint: disable=arguments-differ
        # Strange hook to override sending message to telegram
        # to add parse_mode
        super(ErrBot, self).send_message(mess)  # pylint: disable=bad-super-call
        try:
            self.telegram.sendMessage(mess.to.id, mess.body, parse_mode='Markdown')
        except Exception:
            log.exception(
                "An exception occurred while trying to send the following message "
                "to %s: %s", mess.to.id, mess.body
            )
            raise

    def serve_once_required(self):
        try:
            self.telegram = telegram.Bot(token=self.token)
            me = self.telegram.getMe()
        except telegram.TelegramError as e:
            log.error("Connection failure: %s", e.message)
            return False

        self.bot_identifier = TelegramPerson(
            id=me.id,
            first_name=me.first_name,
            last_name=me.last_name,
            username=me.username
        )

        log.info("Connected")
        return None

    def build_message_identifier(self, txtrep, _message_extras):
        identifier = self.build_identifier(txtrep)
        return identifier
