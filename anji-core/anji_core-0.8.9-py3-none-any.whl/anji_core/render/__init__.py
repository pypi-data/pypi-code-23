__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


def get_render_engine(bot):
    backend = bot.bot_config.BACKEND
    if backend in ('Slack', 'AnjiSlack'):
        from .slack import SlackRenderEngine
        return SlackRenderEngine(bot)
    elif backend in ('Telegram', 'AnjiTelegram'):
        from .telegram import TelegramRenderEngine
        return TelegramRenderEngine(bot)
    elif backend in ('Test', 'AnjiTest'):
        from .test import TestRenderEngine
        return TestRenderEngine(bot)
    else:
        raise Exception('Backend {backend} currently is not supported for render'.format(backend=backend))
