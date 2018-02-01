from errbot import botcmd, Message

from ..cartridges import AbstractCartridge
from ..types import Reaction
from .base import MessageReactionSignal, signal_register

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class SignalCartridge(AbstractCartridge):

    __errdoc__ = 'Signal commands cartirdge to subsrcibe and control to signals'
    name = 'Signal commands'
    technical_name = 'base_signal'
    base_command_prefix = 'signal'

    def get_subscribe_record(self, mess: Message):
        from ..users import User

        technical_name = mess.frm.person
        model = User.query(User.technical_name == technical_name)
        return model[0] if model else User(technical_name=technical_name, name=mess.frm.username, signal_types=[])

    @botcmd(split_args_with=None)
    def signal_subscribe(self, mess, args):
        """
        Subscribe to some signals
        """
        subscribe_record = self.get_subscribe_record(mess)
        subcribable_signal_list = signal_register.get_subscribable_list()
        not_exists_signals = [signal for signal in args if signal not in subcribable_signal_list]
        if not_exists_signals:
            self.shared.render.reply(
                f"Unfortunately, singnals {','.join(not_exists_signals)} not exists!",
                mess
            )
            args = [signal for signal in args if signal not in not_exists_signals]
        if args:
            subscribe_record.signal_types = list(set(args) | set(subscribe_record.signal_types))
            subscribe_record.send()
            self.shared.signals.fire(MessageReactionSignal(mess, Reaction.confirm))
        else:
            self.shared.signals.fire(MessageReactionSignal(mess, Reaction.deny))

    @botcmd(split_args_with=None)
    def signal_unsubscribe(self, mess, args):
        """
        Unsubscribe from some signals
        """
        subscribe_record = self.get_subscribe_record(mess)
        subscribe_record.signal_types = list(set(subscribe_record.signal_types) - set(args))
        subscribe_record.send()
        self.shared.signals.fire(MessageReactionSignal(mess, Reaction.confirm))

    @botcmd(split_args_with=None)
    def signal_list(self, mess, _):
        """
        Print signal subscribe list
        """
        subscribe_record = self.get_subscribe_record(mess)
        if subscribe_record.signal_types:
            self.shared.render.auto_bulleted_list(
                subscribe_record.signal_types,
                title=f'{mess.frm.username} subscribed to signlas',
                in_reply_to=mess
            )
        else:
            self.shared.render.reply('You not subscribed on anything. What to fix it?', mess)

    @botcmd(split_args_with=None)
    def signal_available(self, mess, _):
        """
        Print signals, that you don't use
        """
        subscribe_record = self.get_subscribe_record(mess)
        subcribable_signal_list = signal_register.get_subscribable_list()
        if subscribe_record.signal_types:
            subcribable_signal_list = [signal for signal in subcribable_signal_list if signal not in subscribe_record.signal_types]
        if subcribable_signal_list:
            self.shared.render.auto_bulleted_list(
                subcribable_signal_list,
                title=f'{mess.frm.username} not subscribed to signlas',
                in_reply_to=mess
            )
        else:
            self.shared.render.reply('You subscribed on each signal in systemd!', mess)
