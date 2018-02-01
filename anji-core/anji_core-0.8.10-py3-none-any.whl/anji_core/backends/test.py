import logging
import sys
from threading import Thread

from errbot.backends.test import TestBackend, TestBot
from errbot.bootstrap import setup_bot

import pytest

from anji_core.backend import AnjiBackendMixin

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

log = logging.getLogger('errbot.backends.test')


class AnjiTest(AnjiBackendMixin, TestBackend):

    def serve_once(self) -> None:
        pass

    def build_message_identifier(self, txtrep, _message_extras):
        identifier = self.build_identifier(txtrep)
        return identifier


class AnjiTestBot(TestBot):

    def start(self):
        """
        Start the bot

        Calling this method when the bot has already started will result
        in an Exception being raised.
        """
        if self.bot_thread is not None:
            raise Exception("Bot has already been started")
        # Override to change Test to AnjiTest backend
        self._bot = setup_bot('AnjiTest', self.logger, self.bot_config)
        self.bot_thread = Thread(target=self.bot.serve_forever, name='TestBot main thread')
        self.bot_thread.setDaemon(True)
        self.bot_thread.start()

        self.bot.push_message("!echo ready")

        # Ensure bot is fully started and plugins are loaded before returning
        for _i in range(60):
            #  Gobble initial error messages...
            if self.bot.pop_message(timeout=1) == "ready":
                break
        else:
            raise AssertionError('The "ready" message has not been received (timeout).')


@pytest.fixture(scope='module')
def anjibot(request) -> AnjiTestBot:
    """
    Pytest fixture to write tests against a fully functioning bot.

    For example, if you wanted to test the builtin `!about` command,
    you could write a test file with the following::

        def test_about(testbot):
            testbot.push_message('!about')
            assert "Err version" in testbot.pop_message()

    It's possible to provide additional configuration to this fixture,
    by setting variables at module level or as class attributes (the
    latter taking precedence over the former). For example::

        extra_plugin_dir = '/foo/bar'

        def test_about(testbot):
            testbot.push_message('!about')
            assert "Err version" in testbot.pop_message()

    ..or::

        extra_plugin_dir = '/foo/bar'

        class Tests(object):
            # Wins over `extra_plugin_dir = '/foo/bar'` above
            extra_plugin_dir = '/foo/baz'

            def test_about(self, testbot):
                testbot.push_message('!about')
                assert "Err version" in testbot.pop_message()

    ..to load additional plugins from the directory `/foo/bar` or
    `/foo/baz` respectively. This works for the following items, which are
    passed to the constructor of :class:`~errbot.backends.test.TestBot`:

    * `extra_plugin_dir`
    * `loglevel`
    """

    def on_finish():
        bot.stop()
        bot.anji.register.drop_database()

    #  setup the logging to something digestible.
    logger = logging.getLogger('')
    logging.getLogger('yapsy').setLevel(logging.ERROR)  # this one is way too verbose in debug
    logging.getLogger('MARKDOWN').setLevel(logging.ERROR)  # this one is way too verbose in debug
    logging.getLogger('Rocket.Errors').setLevel(logging.ERROR)  # this one is way too verbose in debug
    logger.setLevel(logging.DEBUG)
    console_hdlr = logging.StreamHandler(sys.stdout)
    console_hdlr.setFormatter(logging.Formatter("%(levelname)-8s %(name)-25s %(message)s"))
    logger.handlers = []
    logger.addHandler(console_hdlr)

    kwargs = {}

    for attr, default in (('extra_plugin_dir', None), ('extra_config', None), ('loglevel', logging.DEBUG),):
        if hasattr(request, 'instance'):
            kwargs[attr] = getattr(request.instance, attr, None)
        if kwargs[attr] is None:
            kwargs[attr] = getattr(request.module, attr, default)

    bot = AnjiTestBot(**kwargs)
    bot.start()
    bot.anji = bot._bot.anji_plugin

    request.addfinalizer(on_finish)
    return bot
