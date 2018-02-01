import textwrap
import inspect

from errbot import botcmd

from ..cartridges import AbstractCartridge

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class HelpCartridge(AbstractCartridge):

    name = 'Help cartridge'
    __errdoc__ = "Cartrige with help commands"
    base_command_prefix = "help"
    technical_name = 'help_help'

    @botcmd(split_args_with=None)
    def help(self, mess, args):
        """
        Provide help information about commands
        """
        if args:
            cartridges = filter(lambda x: x.base_command_prefix in args, self.shared.bot.cartridge_registry.registry.values())
            for cartridge in cartridges:
                with self.shared.render as r:
                    title = f"Cartridge {cartridge.name}"
                    if "commands" not in title.lower():
                        title += " commands"
                    r.title(title)
                    r.reply_to(mess)
                    with r.field_list() as lst:
                        for method_name, class_method in inspect.getmembers(cartridge, predicate=lambda x: inspect.ismethod(x) and hasattr(x, '_err_command')):
                            lst.add(
                                f"{self.shared.bot.prefix}{method_name.replace('_', ' ')}",
                                textwrap.dedent(self.shared.bot.get_doc(class_method)).strip()
                            )
        else:
            with self.shared.render as r:
                r.title('Cartridge list')
                r.reply_to(mess)
                with r.field_list() as lst:
                    for cartridge in self.shared.bot.cartridge_registry.registry.values():
                        lst.add(cartridge.base_command_prefix, cartridge.__errdoc__)
