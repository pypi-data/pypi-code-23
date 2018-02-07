from confmodel.errors import ConfigError
from vumi.message import TransportUserMessage
from vumi.tests.helpers import VumiTestCase

from vumi_unidecode_middleware import UnidecodeMiddleware


class UnidecodeMiddlewareTests(VumiTestCase):
    def make_unidecode_middleware(self, config):
        """
        Creates a fake UnidecodeMiddleware instance for testing.
        """
        worker = object()
        mw = UnidecodeMiddleware("test_unidecode", config, worker)
        mw.setup_middleware()
        self.addCleanup(mw.teardown_middleware)
        return mw

    def make_message(self, content):
        return TransportUserMessage(
            to_addr="45678", from_addr="12345", content=content,
            transport_name="test", transport_type="test")

    def test_make_unidecode_middleware(self):
        """
        The make_unidecode_middleware helper function should return an instance
        of UnidecodeMiddleware
        """
        middleware = self.make_unidecode_middleware({})
        self.assertIsInstance(middleware, UnidecodeMiddleware)

    def test_invalid_message_direction(self):
        """
        If the config contains an invalid message direction, then a config
        error should be raised
        """
        with self.assertRaises(ConfigError) as e:
            self.make_unidecode_middleware({'message_direction': 'foo'})
        self.assertIn('foo', e.exception.message)

    def test_outbound_inbound_messages_not_converted(self):
        """
        If the config is set for outbound messages, then inbound messages
        shouldn't be converted
        """
        middleware = self.make_unidecode_middleware({
            'message_direction': 'outbound',
        })
        message = self.make_message(u"\u201C")
        middleware.handle_inbound(message, "test")
        self.assertEqual(message['content'], u"\u201C")

    def test_inbound_messages_converted(self):
        """
        If the config is set for inbound messages, then inbound messages should
        be converted
        """
        middleware = self.make_unidecode_middleware({
            'message_direction': 'inbound',
        })
        message = self.make_message(u"\u201C")
        middleware.handle_inbound(message, "test")
        self.assertEqual(message['content'], u'"')

    def test_both_messages_converted(self):
        """
        If the config is set for both inbound and outbound messages, then
        inbound and outbound messages should be converted
        """
        middleware = self.make_unidecode_middleware({
            'message_direction': 'both',
        })

        message = self.make_message(u"\u201C")
        middleware.handle_inbound(message, "test")
        self.assertEqual(message['content'], u'"')

        message = self.make_message(u"\u201C")
        middleware.handle_outbound(message, "test")
        self.assertEqual(message['content'], u'"')

    def test_ignore_characters_skips_characters(self):
        """
        If there are ignore characters specified, those characters should not
        be converted
        """
        middleware = self.make_unidecode_middleware({
            'ignore_characters': u"\u201C\u2018",
        })
        message = self.make_message(u"\u201C\u201D\u2018\u2019")
        middleware.handle_inbound(message, "test")
        self.assertEqual(message['content'], u"""\u201C"\u2018'""")

    def test_inbound_outbound_messages_not_converted(self):
        """
        If the config is set for inbound messages, then outbound messages
        shouldn't be converted
        """
        middleware = self.make_unidecode_middleware({
            'message_direction': 'inbound',
        })
        message = self.make_message(u"\u201C")
        middleware.handle_outbound(message, "test")
        self.assertEqual(message['content'], u"\u201C")

    def test_outbound_messages_converted(self):
        """
        If the config is set for outbound messages, then outbound messages
        should be converted
        """
        middleware = self.make_unidecode_middleware({
            'message_direction': 'outbound',
        })
        message = self.make_message(u"\u201C")
        middleware.handle_outbound(message, "test")
        self.assertEqual(message['content'], u'"')
