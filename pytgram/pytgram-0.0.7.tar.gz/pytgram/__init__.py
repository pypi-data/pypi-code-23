"""pytgram package.

Library to create Telegram Bot based on Twisted.

"""


from .api import TelegramBot, MessageHandler, polling
from .webhook import web_hook, set_webhook, delete_webhook, get_webhook_info
from .markup import (
    KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, ForceReply,
    InlineKeyboardMarkup, ReplyKeyboardRemove
)
from .inline import (
    InlineQueryResultLocation, InputContactMessageContent,
    InputLocationMessageContent, InputVenueMessageContent,
    InlineQueryResultMpeg4Gif, InlineQueryResultDocument,
    InlineQueryResultVenue, InlineQueryResultContact, InlineQueryResultGame,
    InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultGif,
    InlineQueryResultVideo, InlineQueryResultVoice, InlineQueryResultPhoto,
    InlineQueryResultAudio,
    InlineQueryResultCachedGif, InlineQueryResultCachedMpeg4Gif,
    InlineQueryResultCachedSticker, InlineQueryResultCachedDocument,
    InlineQueryResultCachedVideo, InlineQueryResultCachedVoice,
    InlineQueryResultCachedAudio, InlineQueryResultCachedPhoto,
)


__version__ = '0.0.7'
__author__ = 'Artem Kustov'
__email__ = 'artem.kustov@artcom-net.ru'
__license__ = 'MIT'
