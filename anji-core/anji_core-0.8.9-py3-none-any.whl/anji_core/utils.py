from functools import wraps, partial

from .types import RenderFeatures, Reaction


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


def command_reaction_decorator(func=None, alternative_text=''):
    @wraps(func)
    def wrapper(self, mess, *args, **kwargs):
        if self.bot.render.is_support(RenderFeatures.reaction):
            self.bot.render.add_reaction(mess, Reaction.processing)
        try:
            result = func(self, mess, *args, **kwargs)
        except Exception:
            if self.bot.render.is_support(RenderFeatures.reaction):
                self.bot.render.remove_reaction(mess, Reaction.processing)
                self.bot.render.add_reaction(mess, Reaction.problem)
            raise
        if self.bot.render.is_support(RenderFeatures.reaction):
            self.bot.render.remove_reaction(mess, Reaction.processing)
            self.bot.render.add_reaction(mess, Reaction.confirm)
        else:
            self.bot.render.reply(alternative_text, mess)
        return result

    if func is None:
        return partial(command_reaction_decorator, alternative_text=alternative_text)

    return wrapper
