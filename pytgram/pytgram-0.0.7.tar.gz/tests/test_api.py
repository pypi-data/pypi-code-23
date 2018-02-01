import types
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web.client import Agent
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.trial import unittest

from pytgram.api import TelegramBot, _get_updates, MessageHandler
from pytgram.content import (
    User, Message, MessageEntity, PhotoSize, Audio, Document, Sticker, Video,
    Voice, Location, Venue, Contact, UserProfilePhotos, File, Chat, ChatMember,
    BadRequest, _Content)
from pytgram.webhook import delete_webhook
from tests import TOKEN, CHAT_ID, CONTACT_NUMBER, USER_ID


bot = TelegramBot(TOKEN)
bot._api._agent = Agent(reactor)


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.port = reactor.listenTCP(0, Site(Resource()))

    def tearDown(self):
        reactor.removeAll()
        return self.port.stopListening()

    def test_message_handler_init_content_single(self):

        @MessageHandler(content=['text'])
        def handler():
            pass

        handler_, content = list(*MessageHandler._handlers.items())
        self.assertIsInstance(handler_, types.FunctionType)
        self.assertIsInstance(content, list)
        self.assertEqual(content[0], 'text')
        MessageHandler._handlers = {}

    def test_message_handler_init_content_multiple(self):

        @MessageHandler(content=['text', 'photo'])
        def handler():
            pass

        handler_, content = list(*MessageHandler._handlers.items())
        self.assertIsInstance(handler_, types.FunctionType)
        self.assertIsInstance(content, list)
        self.assertEqual(content[0], 'text')
        self.assertEqual(content[1], 'photo')
        MessageHandler._handlers = {}

    def test_message_handler_init_command_single(self):

        @MessageHandler(command=['/start'])
        def handler():
            pass

        handler_, content = list(*MessageHandler._handlers.items())
        self.assertIsInstance(handler_, types.FunctionType)
        self.assertIsInstance(content, list)
        self.assertEqual(content[0], '/start')
        MessageHandler._handlers = {}

    def test_message_handler_init_command_multiple(self):

        @MessageHandler(command=['/start', '/end'])
        def handler():
            pass

        handler_, content = list(*MessageHandler._handlers.items())
        self.assertIsInstance(handler_, types.FunctionType)
        self.assertIsInstance(content, list)
        self.assertEqual(content[0], '/start')
        self.assertEqual(content[1], '/end')
        MessageHandler._handlers = {}

    def test_message_handler_init_all_same(self):

        @MessageHandler(content=['text', 'photo'], command=['/start'])
        def handler():
            pass

        handler_, content = list(*MessageHandler._handlers.items())
        self.assertIsInstance(handler_, types.FunctionType)
        self.assertIsInstance(content, list)
        for index, content_ in enumerate(content):
            self.assertEqual(content[index], content_)
        MessageHandler._handlers = {}

    def test_message_handler_init_all_different(self):

        @MessageHandler(content=['text', 'photo'])
        def content_handler():
            pass

        @MessageHandler(command=['/start', '/end'])
        def command_handler():
            pass

        content, command = MessageHandler._handlers.items()
        for func in (content[0], command[0]):
            self.assertIsInstance(func, types.FunctionType)
        self.assertIsNot(content[0], command[0])
        contents = content[1] + command[1]
        self.assertEqual(contents[0], 'text')
        self.assertEqual(contents[1], 'photo')
        self.assertEqual(contents[2], '/start')
        self.assertEqual(contents[3], '/end')

        MessageHandler._handlers = {}

    def test_message_handler_init_command_without_slash(self):

        @MessageHandler(command=['start', 'end'])
        def handler():
            pass

        for command in list(*MessageHandler._handlers.values()):
            self.assertEqual(command[0], '/')
        MessageHandler._handlers = {}

    def test_message_handler_get_handler_single(self):

        @MessageHandler(content=['text'])
        def handler():
            pass

        message = Message(
            **{'message_id': 5102,
               'date': 14925053,
               'chat': {'id': 72340936, 'type': 'private', 'first_name': ''},
               'from': {'id': 72340936, 'first_name': 'Artem'},
               'text': 'some_text'}
        )
        handler = MessageHandler._get_handler(message)
        self.assertIsInstance(handler, types.FunctionType)
        MessageHandler._handlers = {}

    def test_message_handler_get_handler_same(self):
        @MessageHandler(content=['text', 'photo'])
        def handler():
            pass

        message = Message(
            **{'message_id': 5102,
               'date': 14925053,
               'chat': {'id': 72340936, 'type': 'private',
                        'first_name': ''},
               'from': {'id': 72340936, 'first_name': 'Artem'},
               'text': 'some_text'}
        )
        handler_text = MessageHandler._get_handler(message)
        message.content_type = 'photo'
        handler_photo = MessageHandler._get_handler(message)
        self.assertIs(handler_text, handler_photo)
        self.assertIsInstance(handler_text, types.FunctionType)
        MessageHandler._handlers = {}

    def test_message_handler_get_handler_different(self):

        @MessageHandler(content=['text'])
        def text_handler():
            pass

        @MessageHandler(content=['photo'])
        def photo_handler():
            pass

        message = Message(
            **{'message_id': 5102,
               'date': 14925053,
               'chat': {'id': 72340936, 'type': 'private',
                        'first_name': ''},
               'from': {'id': 72340936, 'first_name': 'Artem'},
               'text': 'some_text'}
        )
        handler_text = MessageHandler._get_handler(message)
        message.content_type = 'photo'
        handler_photo = MessageHandler._get_handler(message)

        self.assertIsInstance(handler_text, types.FunctionType)
        self.assertIsInstance(handler_photo, types.FunctionType)
        self.assertIsNot(handler_text, handler_photo)
        MessageHandler._handlers = {}

    def test_message_handler_get_handler_command(self):

        @MessageHandler(command=['start'])
        def text_handler():
            pass

        @MessageHandler(command=['/end'])
        def photo_handler():
            pass

        message = Message(
            **{'message_id': 5102,
               'date': 14925053,
               'chat': {'id': 72340936, 'type': 'private',
                        'first_name': ''},
               'from': {'id': 72340936, 'first_name': 'Artem'},
               'text': '/start'}
        )
        handler_start = MessageHandler._get_handler(message)
        message.text = '/end'
        handler_end = MessageHandler._get_handler(message)
        self.assertIsNot(handler_start, handler_end)
        self.assertIsInstance(handler_start, types.FunctionType)
        self.assertIsInstance(handler_end, types.FunctionType)
        MessageHandler._handlers = {}

    def test_message_handler_get_handler_all(self):

        @MessageHandler(content=['text', 'photo'])
        def content_handler():
            pass

        @MessageHandler(command=['start, /end'])
        def command_handler():
            pass

        message = Message(
            **{'message_id': 5102,
               'date': 14925053,
               'chat': {'id': 72340936, 'type': 'private',
                        'first_name': ''},
               'from': {'id': 72340936, 'first_name': 'Artem'},
               'text': 'some_text'}
        )
        handler_text = MessageHandler._get_handler(message)
        message.content_type = 'photo'
        handler_photo = MessageHandler._get_handler(message)
        self.assertIs(handler_text, handler_photo)
        message.content_type = 'text'
        message.text = '/start'
        handler_start = MessageHandler._get_handler(message)
        message.text = '/end'
        handler_end = MessageHandler._get_handler(message)
        self.assertIs(handler_start, handler_end)
        self.assertIsNot(handler_text, handler_start)
        MessageHandler._handlers = {}

    @inlineCallbacks
    def test_get_updates(self):
        delete_webhook(TOKEN)
        result = yield bot.get_updates()
        self.assertIsInstance(result, list)
        return result

    @inlineCallbacks
    def test__get_updates(self):
        delete_webhook(TOKEN)

        def check_assert(message):
            if message:
                self.assertIsInstance(message, _Content)

        yield _get_updates(bot, check_assert)

    @inlineCallbacks
    def test_get_me(self):
        result = yield bot.get_me()
        self.assertIsInstance(result, User)
        return result

    @inlineCallbacks
    def test_send_text(self):
        result = yield bot.send_message(chat_id=CHAT_ID, text='test text..')
        self.assertIsInstance(result, Message)
        self.assertEqual(result.content_type, 'text')
        return result

    @inlineCallbacks
    def test_markdown_bold(self):
        result = yield bot.send_message(chat_id=CHAT_ID, text='*test text..*',
                                        parse_mode='Markdown')
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'bold')
        return result

    @inlineCallbacks
    def test_markdown_italic(self):
        result = yield bot.send_message(chat_id=CHAT_ID, text='_test text.._',
                                        parse_mode='Markdown')
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'italic')
        return result

    @inlineCallbacks
    def test_markdown_link(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='[Google](https://google.com/)',
            parse_mode='Markdown'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'text_link')
        yield result

    @inlineCallbacks
    def test_markdown_code(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='`test text`',
            parse_mode='Markdown'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'code')
        yield result

    @inlineCallbacks
    def test_markdown_pre(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='```test text```',
            parse_mode='Markdown'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'pre')
        yield result

    @inlineCallbacks
    def test_html_bold(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<b>test text..</b>',
            parse_mode='HTML'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'bold')
        yield result

    @inlineCallbacks
    def test_html_strong(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<strong>test text..</strong>',
            parse_mode='HTML'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'bold')
        yield result

    @inlineCallbacks
    def test_html_italic(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<i>test text..</i>',
            parse_mode='HTML'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'italic')
        yield result

    @inlineCallbacks
    def test_html_em(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<em>test text..</em>',
            parse_mode='HTML'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'italic')
        yield result

    @inlineCallbacks
    def test_html_link(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<a href="https://google.com/">Google</a>',
            parse_mode='HTML',
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'text_link')
        yield result

    @inlineCallbacks
    def test_html_code(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<code>test text..</code>',
            parse_mode='HTML'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'code')
        yield result

    @inlineCallbacks
    def test_html_code(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID,
            text='<pre>test text..</pre>',
            parse_mode='HTML'
        )
        self.assertIsInstance(result, Message)
        for entity in result.entities:
            self.assertIsInstance(entity, MessageEntity)
            self.assertEqual(entity.type, 'pre')
        yield result

    @inlineCallbacks
    def test_send_bad_request_chat_id(self):
        result = yield bot.send_message(
            text='Some text..'
        )
        self.assertIsInstance(result, BadRequest)
        yield result

    @inlineCallbacks
    def test_send_bad_request_text(self):
        result = yield bot.send_message(
            chat_id=CHAT_ID
        )
        self.assertIsInstance(result, BadRequest)
        yield result

    @inlineCallbacks
    def test_forward_message(self):
        result = yield bot.forward_message(chat_id=CHAT_ID,
                                           from_chat_id=CHAT_ID, message_id=67)
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.forward_from, User)
        return result

    @inlineCallbacks
    def test_forward_message_bad_request_chat_id(self):
        result = yield bot.forward_message(from_chat_id=CHAT_ID, message_id=67)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_forward_message_bad_request_from(self):
        result = yield bot.forward_message(chat_id=CHAT_ID, message_id=67)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_forward_message_bad_request_message_id(self):
        result = yield bot.forward_message(chat_id=CHAT_ID,
                                           from_chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_photo_from_url(self):
        result = yield bot.send_photo(
            chat_id=CHAT_ID,
            photo='http://datareview.info/wp-content/uploads/Python.png'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.photo, list)
        for photo in result.photo:
            self.assertIsInstance(photo, PhotoSize)
        return result

    @inlineCallbacks
    def test_send_photo_from_id(self):
        result = yield bot.send_photo(
            chat_id=CHAT_ID,
            photo='AgADBAAD-D01G9QZZAdmaz0WDufh8g9dYRkABFVcYUMtNqj1TBQCAAEC'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.photo, list)
        for photo in result.photo:
            self.assertIsInstance(photo, PhotoSize)
        return result

    @inlineCallbacks
    def test_send_photo_from_file(self):
        result = yield bot.send_photo(
            chat_id=CHAT_ID,
            photo='files/python2.png',
        )
        print(result.__dict__)
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.photo, list)
        for photo in result.photo:
            self.assertIsInstance(photo, PhotoSize)
        return result

    @inlineCallbacks
    def test_send_photo_bad_request_chat_id(self):
        result = yield bot.send_photo(photo='files/python.png')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_photo_bad_request_photo(self):
        result = yield bot.send_photo(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_audio_from_url(self):
        result = yield bot.send_audio(
            chat_id=CHAT_ID,
            audio='https://dl.last.fm/static/1490498411/131211148/302f3b77ced4'
                  'e5993242f1afa97504029781d48f72b32783b08c46600e9c412a/Death+'
                  'Grips+-+Get+Got.mp3'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.audio, Audio)
        return result

    @inlineCallbacks
    def test_send_audio_from_id(self):
        result = yield bot.send_audio(
            chat_id=CHAT_ID,
            audio='CQADBAADb3MAAlsbZAdbQ7-uVr0tLwI'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.audio, Audio)
        return result

    @inlineCallbacks
    def test_send_audio_from_file(self):
        result = yield bot.send_audio(
            chat_id=CHAT_ID,
            audio='files/test.mp3',
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.audio, Audio)
        return result

    @inlineCallbacks
    def test_send_audio_bad_request_chat_id(self):
        result = yield bot.send_audio(audio='files/test.mp3')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_audio_bad_request_audio(self):
        result = yield bot.send_audio(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_document_from_url(self):
        result = yield bot.send_document(
            chat_id=CHAT_ID,
            document='http://www.pdf995.com/samples/pdf.pdf'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.document, Document)
        return result

    @inlineCallbacks
    def test_send_document_from_id(self):
        result = yield bot.send_document(
            chat_id=CHAT_ID,
            document='BQADBAADtXQAAjEdZAcIYnoFmaaHPQI'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.document, Document)
        return result

    @inlineCallbacks
    def test_send_document_from_file(self):
        result = yield bot.send_document(
            chat_id=CHAT_ID,
            document='files/test.pdf',
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.document, Document)
        return result

    @inlineCallbacks
    def test_send_document_bad_request_chat_id(self):
        result = yield bot.send_document(document='files/test.pdf')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_document_bad_request_document(self):
        result = yield bot.send_document(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_sticker_from_url(self):
        result = yield bot.send_sticker(
            chat_id=CHAT_ID,
            sticker='https://dl.airtable.com/aeRVgwZVQAatdFMFTgQt_sticker.webp'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.sticker, Sticker)
        return result

    @inlineCallbacks
    def test_send_sticker_from_id(self):
        result = yield bot.send_sticker(
            chat_id=CHAT_ID,
            sticker='CAADBAADCXcAAmgdZAexOLCCZ6nZSQI'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.sticker, Sticker)
        return result

    @inlineCallbacks
    def test_send_sticker_from_file(self):
        result = yield bot.send_sticker(
            chat_id=CHAT_ID,
            sticker='files/test.webp',
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.sticker, Sticker)
        return result

    @inlineCallbacks
    def test_send_sticker_bad_request_chat_id(self):
        result = yield bot.send_sticker(sticker='files/test.webp')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_sticker_bad_reqsend_sticker(self):
        result = yield bot.send_sticker(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_video_from_url(self):
        result = yield bot.send_video(
            chat_id=CHAT_ID,
            video='https://player.vimeo.com/external/121564055.hd.mp4?s=646d40'
                  'c18c3c7884f8a350d704b2242a06f3dce6&profile_id=113&oauth2_to'
                  'ken_id=57447761'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.video, Video)
        return result

    @inlineCallbacks
    def test_send_video_from_id(self):
        result = yield bot.send_video(
            chat_id=CHAT_ID,
            video='BAADBAADgXcAAj4ZZAdxW3R2uqABJAI'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.video, Video)
        return result

    @inlineCallbacks
    def test_send_video_from_file(self):
        result = yield bot.send_video(
            chat_id=CHAT_ID,
            video='files/test.mp4',
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.video, Video)
        return result

    @inlineCallbacks
    def test_send_video_bad_request_chat_id(self):
        result = yield bot.send_video(video='files/test.mp4')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_video_bad_request_video(self):
        result = yield bot.send_video(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_voice_from_url(self):
        result = yield bot.send_voice(
            chat_id=CHAT_ID,
            voice='files/test.ogg'
        )
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.voice, Voice)
        return result

    @inlineCallbacks
    def test_send_voice_bad_request_chat_id(self):
        result = yield bot.send_voice(voice='files/test.ogg')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_voice_bad_request_voice(self):
        result = yield bot.send_voice(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_location(self):
        result = yield bot.send_location(chat_id=CHAT_ID, latitude=40.68973,
                                         longitude=-74.0448)
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.location, Location)
        return result

    @inlineCallbacks
    def test_send_location_bad_request_chat_id(self):
        result = yield bot.send_location(latitude=40.68973, longitude=-74.0448)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_location_bad_request_location(self):
        result = yield bot.send_location(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_venue(self):
        result = yield bot.send_venue(chat_id=CHAT_ID, latitude=40.68973,
                                      longitude=-74.0448,
                                      title='Some Title',
                                      address='Some street 60')
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.venue, Venue)
        return result

    @inlineCallbacks
    def test_send_venue_bad_request_chat_id(self):
        result = yield bot.send_venue(latitude=40.68973, longitude=-74.0448,
                                      title='Some Title', address='Address')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_venue_bad_request_venue(self):
        result = yield bot.send_venue(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_contact(self):
        result = yield bot.send_contact(chat_id=CHAT_ID,
                                        phone_number=CONTACT_NUMBER,
                                        first_name='Artem')
        self.assertIsInstance(result, Message)
        self.assertIsInstance(result.contact, Contact)
        return result

    @inlineCallbacks
    def test_send_contact_bad_request_chat_id(self):
        result = yield bot.send_contact(phone_number=CONTACT_NUMBER,
                                        first_name='Artem')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_contact_bad_request_contact(self):
        result = yield bot.send_contact(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_chat_action_typing(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID, action='typing')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_upload_photo(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='upload_photo')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_record_video(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='record_video')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_upload_video(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='upload_video')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_record_audio(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='record_audio')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_upload_audio(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='upload_audio')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_upload_document(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='upload_document')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_find_location(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID,
                                            action='find_location')
        self.assertIs(result, True)
        return result

    @inlineCallbacks
    def test_send_chat_action_bad_request_chat_id(self):
        result = yield bot.send_chat_action(action='typing')
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_send_chat_action_bad_request_chat_action(self):
        result = yield bot.send_chat_action(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_get_user_profile_photos(self):
        result = yield bot.get_user_profile_photos(user_id=USER_ID)
        self.assertIsInstance(result, UserProfilePhotos)
        return result

    @inlineCallbacks
    def test_get_user_profile_photos_bad_request_user_id(self):
        result = yield bot.get_user_profile_photos()
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_get_file(self):
        result = yield bot.get_file(file_id='AgADBAAD-D01G9QZZAdmaz0WDufh8g9dY'
                                            'RkABFVcYUMtNqj1TBQCAAEC')
        self.assertIsInstance(result, File)
        return result

    @inlineCallbacks
    def test_get_file_bad_request_file_id(self):
        result = yield bot.get_file()
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_get_chat(self):
        result = yield bot.get_chat(chat_id=CHAT_ID)
        self.assertIsInstance(result, Chat)
        return result

    @inlineCallbacks
    def test_get_chat_bad_request_chat_id(self):
        result = yield bot.get_chat()
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_get_chat_member(self):
        result = yield bot.get_chat_member(chat_id=CHAT_ID, user_id=USER_ID)
        self.assertIsInstance(result, ChatMember)
        return result

    @inlineCallbacks
    def test_get_chat_member_bad_request_chat_id(self):
        result = yield bot.get_chat_member(user_id=USER_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_get_chat_member_bad_request_user_id(self):
        result = yield bot.get_chat_member(chat_id=CHAT_ID)
        self.assertIsInstance(result, BadRequest)
        return result

    @inlineCallbacks
    def test_edit_message_text(self):
        message = yield bot.send_message(chat_id=CHAT_ID, text='before edit..')
        result = yield bot.edit_message_text(chat_id=CHAT_ID,
                                             text='after edit..',
                                             message_id=message.id)
        self.assertIsInstance(result, Message)
        return result

    @inlineCallbacks
    def test_edit_maessage_caption(self):
        message = yield bot.send_photo(
            chat_id=CHAT_ID,
            photo='AgADBAAD-D01G9QZZAdmaz0WDufh8g9dYRkABFVcYUMtNqj1TBQCAAEC',
            caption='Before caption..'
        )
        result = yield bot.edit_message_caption(chat_id=CHAT_ID,
                                                caption='after caption..',
                                                message_id=message.id)
        self.assertIsInstance(result, Message)
        return result
