from anji_orm import Model, StringField, DictField
from errbot.backends.base import Message as ErrbotMessage

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class Message(Model):

    _table = 'messages'

    frm = StringField()
    to = StringField()
    body = StringField()
    extras = DictField()

    def to_errbot_message(self):
        return ErrbotMessage(
            body=self.body,
            frm=self.shared.bot.build_identifier(self.frm, message_extras=self.extras),
            to=self.shared.bot.build_identifier(self.to, message_extras=self.extras),
            extras=self.extras
        )

    @classmethod
    def from_errbot_message(cls, message):
        message = cls(
            frm=str(message.frm),
            to=str(message.to),
            body=message.body,
            extras=message.extras
        )
        message.send()
        return message
