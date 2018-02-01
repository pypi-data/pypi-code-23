from errbot import botcmd

from ..cartridges import AbstractCartridge
from ..types import Reaction, RenderFeatures

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


REACTION_FAQ = {
    Reaction.confirm: 'Command or command task was executed successul',
    Reaction.deny: 'Command execution impossible',
    Reaction.processing: 'Command or command task execution started',
    Reaction.accepted: 'Task for command was created and queued',
    Reaction.problem: 'Task execution problem',
    Reaction.processing_next: 'Awaiting next flow step',
    Reaction.empty: 'This command cannot do anything',
    Reaction.blocked: 'Execution of this command was blocked by security subsystem'
}


class FAQCartridge(AbstractCartridge):

    name = 'FAQ cartridge'
    __errdoc__ = "Cartrige with FAQ for bot functions"
    base_command_prefix = "faq"
    technical_name = 'help_faq'

    @botcmd(split_args_with=None)
    def faq_reactions(self, mess, _args):
        if self.shared.render.is_support(RenderFeatures.reaction):
            with self.shared.render as r:
                r.title("List of reaction with descripton")
                r.reply_to(mess)
                with r.field_list() as lst:
                    for key, value in REACTION_FAQ.items():
                        lst.add(r.raw_reaction(key), value)
        else:
            self.shared.render.reply(
                "This chat don't support reaction, sempai! I cannot draw this FAQ for you.",
                mess
            )
