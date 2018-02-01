import re

from .base import AbstractRenderEngine, UnsupportedFeatureException

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

MD_ESCAPE_TELEGRAM_RE = re.compile('|'.join(re.escape(c) for c in ('\\', '`', '*', '_', '[', ']', '>', '#', '+')))


class TelegramRenderEngine(AbstractRenderEngine):

    defaut_escape_logic = True

    def md_escape(self, txt):
        """ Call this if you want to be sure your text won't be interpreted as markdown
        :param txt: bare text to escape.
        """
        return MD_ESCAPE_TELEGRAM_RE.sub(lambda match: '\\' + match.group(0), txt)

    def reply(self, message, target_message, escape_markdown=True):
        if target_message:
            if escape_markdown:
                message = self.md_escape(message)
            self.bot.send_simple_reply(target_message, message, threaded=True)
        else:
            self.send(message, escape_markdown=escape_markdown)

    def send(self, message, escape_markdown=True, channel=None):
        if escape_markdown:
            message = self.md_escape(message)
        if channel is None:
            channel = self.bot['default_channel']
        self.bot.send(
            self.bot.build_identifier(channel),
            message
        )

    def flush(self):
        text_results = []
        if self._message_title:
            text_results.append('*{}*'.format(self.md_escape(self._message_title)))
        for custom_object in self.custom_objects:
            text_results.append(custom_object.render_markdown())
        self.send("\n\n".join(text_results), escape_markdown=False)

    def add_reaction(self, message, reaction):
        raise UnsupportedFeatureException("Telegram cannot render reactions! Please, use is_support function to check")

    def remove_reaction(self, message, reaction):
        raise UnsupportedFeatureException("Telegram cannot render reactions! Please, use is_support function to check")

    def raw_reaction(self, reaction):
        raise UnsupportedFeatureException("Telegram cannot render reactions! Please, use is_support function to check")

    def is_support(self, render_feature):
        return False
