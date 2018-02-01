from anji_orm import StringField, ListField, BooleanField
from errbot import arg_botcmd, botcmd

from .security import guard
from .signals import MessageReactionSignal
from .cartridges import AbstractCartridge
from .types import Reaction
from .manager import ManagedModel, BaseManager

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class User(ManagedModel):

    _table = 'users'
    display_name = 'user'

    name = StringField(description='Username', displayed=False)
    signal_types = ListField(description='List of listened signals', service=True)
    is_authorized = BooleanField(description='Does user authorized by administrator', service=True)


class UserCartridge(AbstractCartridge):

    __errdoc__ = 'Core commands to control users'
    name = 'Users Cartridge'
    technical_name = 'core_users'
    base_command_prefix = 'user'

    @botcmd
    def user_register(self, mess, _args):
        user = User.query(User.technical_name == mess.frm.person)
        if user:
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.empty,
                    alternative_text='You already exists in system'
                )
            )
        else:
            User(technical_name=mess.frm.person, name=mess.frm.username).send()
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.confirm,
                    alternative_text='You registered in system!'
                )
            )

    @arg_botcmd('users', type=str, nargs='*', help='Usernames to approve')
    @guard.admin_only_command
    def user_approve(self, mess, users):
        user_records = User.query(
            (User.is_authorized == False) &  # pylint: disable=singleton-comparison
            (User.name.one_of(*users))
        )
        if user_records:
            for user in user_records:
                user.is_authorized = True
                user.send()
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.confirm,
                    alternative_text='Users was successfuly activated'
                )
            )
        else:
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.empty,
                    alternative_text='Each user already activated or not exists'
                )
            )


class UserManager(BaseManager):

    controlled_model = User
    controlled_cartridge = UserCartridge
    control_prefix = 'user'
    autoload_enabled = False
    control_commands_enable = False

    @property
    def manager_short_name(self) -> str:
        return "user"
