from .base import AbstractRenderEngine, UnsupportedFeatureException

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class TestRenderEngine(AbstractRenderEngine):

    def md_escape(self, txt):
        return txt

    def reply(self, message, target_message, escape_markdown=True):
        self.send(message, escape_markdown=escape_markdown)

    def send(self, message, escape_markdown=True, channel=None):
        self.bot.send(
            self.bot.build_identifier('Err'),
            message
        )

    def flush(self):
        text_results = []
        if self._message_title:
            text_results.append('## {}'.format(self._message_title))
        for custom_object in self.custom_objects:
            text_results.append(custom_object.render_plain())
        self.send("\n\n".join(text_results), escape_markdown=False)

    def add_reaction(self, message, reaction):
        raise UnsupportedFeatureException("Test cannot render reactions! Please, use is_support function to check")

    def remove_reaction(self, message, reaction):
        raise UnsupportedFeatureException("Test cannot render reactions! Please, use is_support function to check")

    def raw_reaction(self, reaction):
        raise UnsupportedFeatureException("Test cannot render reactions! Please, use is_support function to check")

    def is_support(self, render_feature):
        return False
