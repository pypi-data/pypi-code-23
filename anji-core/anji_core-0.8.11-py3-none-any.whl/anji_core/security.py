import inspect

from anji_orm import prettify_value

from .types import SecurityModel, Reaction
from .signals import MessageReactionSignal

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

SECURITY_COMMAND_RULES_STORAGE_KEY = 'security_command_rules'


class SecurityGuard(object):

    def __init__(self):
        self._secutiry_command_rules = {}
        self.bot = None

    def init_with_bot(self, bot):
        self.bot = bot

    def update_from_storage(self):
        stored_security_command_rules = self.bot.get(SECURITY_COMMAND_RULES_STORAGE_KEY)
        if stored_security_command_rules:
            stored_security_command_rules = {k: SecurityModel.search(v) for k, v in stored_security_command_rules.items()}
            self._secutiry_command_rules.update(stored_security_command_rules)
        self.bot[SECURITY_COMMAND_RULES_STORAGE_KEY] = prettify_value(self._secutiry_command_rules)

    def admin_only_command(self, function):
        self._secutiry_command_rules[function.__name__] = SecurityModel.admin_only
        return function

    def for_authorized_users(self, function):
        self._secutiry_command_rules[function.__name__] = SecurityModel.for_authorized_users
        return function

    def default_for_command(self, function, security_model):
        self._secutiry_command_rules.setdefault(function.__name__, security_model)

    def process_command_from_cartridges(self):
        for _, cartridge_object in self.bot.cartridge_registry.registry.items():
            default_command_security_policy = cartridge_object.default_command_security_policy
            for _, command_function in inspect.getmembers(cartridge_object, lambda x: hasattr(x, '_err_command')):
                self.default_for_command(command_function, default_command_security_policy)
        self.bot[SECURITY_COMMAND_RULES_STORAGE_KEY] = prettify_value(self._secutiry_command_rules)

    def check_security_rule(self, user_technical_name, protection_level):
        from .users import User

        if user_technical_name in self.bot.bot_config.BOT_ADMINS:
            return True
        if protection_level == SecurityModel.admin_only:
            return False
        elif protection_level == SecurityModel.for_authorized_users:
            user = User.query(User.technical_name == user_technical_name)
            user = user[0]
            if not user.is_authorized:
                return False
        return True

    def validate_command(self, msg, cmd, args):
        protection_level = SecurityModel.max(
            self._secutiry_command_rules.get(cmd, SecurityModel.free_for_anyone),
            self.bot.bot_config.ANJI_GLOBAL_SECURITY_MODEL
        )
        if self.check_security_rule(msg.frm.person, protection_level):
            return msg, cmd, args
        self.bot.manager_env['users'].create_record(technical_name=msg.frm.person, name=msg.frm.username)
        self.bot.signals.fire(MessageReactionSignal(msg, Reaction.blocked))
        return None, None, None


guard = SecurityGuard()
