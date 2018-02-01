"""api module.

This module contains the entities needed to work with Telegram Bot API.

"""


import re
import sys
import json
from io import BytesIO
from functools import wraps

import requests
from twisted.internet import reactor, threads, task, _sslverify
from twisted.internet.error import ConnectionDone
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.protocol import Protocol
from twisted.web.http_headers import Headers
from twisted.web.client import Agent, FileBodyProducer, HTTPConnectionPool

from .url import get_url
from .content import (
    DictItem, BadRequest, Update, User, Message, UserProfilePhotos, File, Chat,
    ChatMember, GameHighScore, _Query, StickerSet
)


_update_id = 0

if sys.platform == 'win32':
    _sslverify.platformTrust = lambda: None


def _api_request(return_type=None):
    """Decorator for API methods.

    :param return_type: Return type.
    :return: Instance of return_type list objects or BadRequest or True.

    """
    def inner(func):
        @inlineCallbacks
        @wraps(func)
        def wrapper(bot_obj, **kwargs):
            api_method = ''.join(func.__name__.split('_'))
            response = yield bot_obj._api.request(api_method, **kwargs)
            if isinstance(response, BadRequest):
                obj = response
            else:
                response_dict = json.loads(response.decode())
                try:
                    obj_args = response_dict['result']
                    if isinstance(obj_args, dict):
                        obj = return_type(**obj_args)
                    elif isinstance(obj_args, list):
                        obj = return_type.from_list(response_dict['result'])
                    else:
                        obj = obj_args
                except KeyError:
                    obj = BadRequest(response_dict['error_code'],
                                     response_dict['description'],
                                     response_dict.get('parameters', None))
            return obj
        return wrapper
    return inner


@inlineCallbacks
def _get_updates(bot, handler=None, **kwargs):
    """Calls the method get_updates. Uses in polling mode only.

    :param bot: TelegramBot instance.
    :param handler: Function.
    :param kwargs: kwargs for get_updates method, without offset.
    :return: Deferred.

    """
    global _update_id
    handler = handler or MessageHandler.handler
    updates = yield bot.get_updates(offset=_update_id + 1, **kwargs)
    if isinstance(updates, BadRequest):
        raise APIRequestError(updates.__dict__)
    if updates:
        if _update_id == 0:
            _update_id = updates[-1].id
            yield _get_updates(bot, handler, **kwargs)
        _update_id = updates[-1].id
        obj_list = [update.content for update in updates]
        for obj in obj_list:
            yield handler(obj)


def polling(bot, interval=10, handler=None, **kwargs):
    """Starts polling.

    :param bot: TelegramBot instance.
    :param interval: Polling interval in seconds.
    :param handler: Function. If uses, then MessageHandler decorator
        will not be works. It's need if you want handling all messages in one
        function.
    :param kwargs: kwargs for get_updates method, without offset.

    """
    task.LoopingCall(_get_updates, bot, handler, **kwargs).start(interval)


class APIRequestError(Exception):
    pass


class MessageHandler(object):
    """This class is a decorator for functions-handlers defined by the user.
    The purpose of this entity is to store the handlers associated with a
    content type and extract their.

    """
    _handlers = {}

    def __init__(self, content=None, command=None):
        """Initial instance.

        :param content: List of content names.
            Available content names: text, photo, audio, video, video_note,
            document, sticker, voice, contact, location, venue, game, invoice,
            successful_payment, inline_query, callback_query, shipping_query,
            pre_checkout_query, chosen_inline_result.
        :param command: List of command names.

        """
        self._content = content
        if command:
            for index, cmd in enumerate(command):
                if cmd[0] != '/':
                    command[index] = '/' + cmd
        self._command = command

    def __call__(self, func):
        if all((self._content, self._command)):
            content_list = self._content + self._command
        else:
            content_list = self._content or self._command
        MessageHandler._handlers[func] = content_list

    @staticmethod
    def handler(message):
        """Calls handler.

        :param message: input object.
        :return: Deferred.

        """
        deferred = threads.deferToThread(MessageHandler._get_handler, message)

        @inlineCallbacks
        def run_handler(handler):
            if handler:
                yield handler(message)

        deferred.addCallback(run_handler)
        return deferred

    @staticmethod
    def _get_handler(message):
        """Gets handler by content.

        :param message: input object.
        :return: func or None.

        """
        content = None
        command = None
        if isinstance(message, _Query):
            content = message.get_str_type()
        if not content:
            content = message.content_type
            if content == 'text':
                command = message.text if message.text[0] == '/' else None
        content_handler, command_handler = map(
            MessageHandler._get_content_handler, (content, command)
        )
        if content_handler is command_handler:
            handler = command_handler
        elif command and not command_handler:
            handler = None
        else:
            handler = command_handler or content_handler
        return handler

    @staticmethod
    def _get_content_handler(content):
        """Searching for the handler.

        :param content: content type name.
        :return: func or None.

        """
        handler = None
        for func, content_list in MessageHandler._handlers.items():
            if content in content_list:
                handler = func
                break
        return handler


class _HTTPClientProtocol(Protocol):
    """Class for gets payload from response."""

    def __init__(self, deferred):
        self.deferred = deferred
        self.data = b''

    def dataReceived(self, data):
        self.data += data

    def connectionLost(self, reason=ConnectionDone):
        self.deferred.callback(self.data)


class _APIRequest(object):
    """Class for requesting the API."""

    _url = get_url()
    _HEADERS = Headers({'Content-Type': ['application/json']})
    _UPLOAD_METHODS = ('sendphoto', 'sendaudio', 'sendvideo',
                       'senddocument', 'sendsticker', 'sendvoice',
                       'sendvideonote', 'setchatphoto', 'uploadstickerfile',
                       'createnewstickerset', 'addstickertoset')
    _POST_METHODS = ('send', 'forward', 'kick', 'leave', 'pin', 'unpin', 'add',
                     'unban', 'answer', 'edit', 'delete', 'set', 'upload',
                     'create')

    def __init__(self, token):
        """Initial instance.

        :param token: Bot token.

        """
        self._agent = Agent(reactor, pool=HTTPConnectionPool(reactor))
        _APIRequest._url = _APIRequest._url.format(token=token,
                                                   method='{method}')

    def request(self, api_method, **kwargs):
        """Makes request to the API.

        :param api_method: API method name.
        :param kwargs: method arguments.

        :return: Deferred.

        """
        deferred = threads.deferToThread(self._get_request_args, api_method,
                                         **kwargs)

        def _request(req_data):
            if not isinstance(req_data, BadRequest):
                if 'files' in req_data:
                    res_finished = threads.deferToThread(self._upload_request,
                                                         **req_data)
                else:
                    res_deferred = self._agent.request(**req_data)

                    def response_handler(response, dfd):
                        response.deliverBody(_HTTPClientProtocol(dfd))

                    res_finished = Deferred()
                    res_deferred.addCallback(response_handler, res_finished)
            else:
                res_finished = req_data
            return res_finished

        deferred.addCallback(_request)
        return deferred

    @staticmethod
    def _upload_request(**kwargs):
        """Uses for upload files.

        :param kwargs: request args.
        :return bytes.

        """
        return requests.post(**kwargs).content

    @staticmethod
    def _get_url(api_method):
        return _APIRequest._url.format(method=api_method)

    @staticmethod
    def _get_request_args(api_method, **kwargs):
        """Gets arguments for request.

        :param api_method: API method name.
        :param kwargs: method arguments.
        :return: dictionary with the arguments or BadRequest.

        """
        req_data = {}
        if api_method in _APIRequest._UPLOAD_METHODS:
            content = api_method.replace('send', '')
            try:
                upload_source = kwargs[content]
            except KeyError:
                req_data = BadRequest(400, '{} is empty'.format(content))
            else:
                is_file_path = bool(re.search(r'\.[a-zA-Z0-9]+$',
                                              upload_source))
                if is_file_path and not upload_source.startswith('http'):
                    kwargs.pop(content)
                    file = {content: open(upload_source, 'rb')}
                    req_data = {
                        'url': _APIRequest._get_url(api_method),
                        'data': kwargs,
                        'files': file,
                    }
        if not req_data:
            if list(
                filter(lambda method: api_method.startswith(method),
                       _APIRequest._POST_METHODS)
            ):
                req_method = b'POST'
            else:
                req_method = b'GET'
            url = _APIRequest._get_url(api_method).encode()
            body = None
            if kwargs:
                for arg, value in kwargs.items():
                    if isinstance(value, DictItem):
                        kwargs[arg] = value.to_dict()
                    elif isinstance(value, (list, tuple)):
                        obj_list = [obj.to_dict() for obj in value
                                    if isinstance(obj, DictItem)]
                        kwargs[arg] = obj_list or kwargs[arg]
                body = FileBodyProducer(
                    BytesIO(json.dumps(kwargs).encode())
                )
            req_data = {
                'method': req_method,
                'uri': url,
                'headers': _APIRequest._HEADERS,
                'bodyProducer': body
            }
        return req_data


class TelegramBot(object):
    """This class represents Telegram bot."""

    def __init__(self, token):
        """Initial instance.

        :param token: Bot token.

        """
        self.token = token
        self._api = _APIRequest(self.token)

    def __str__(self):
        return '{}(token:{})'.format(self.__class__.__name__, self.token)

    @_api_request(return_type=Update)
    def get_updates(self, offset=None, limit=None, timeout=None,
                    allowed_updates=None):
        """Use this method to receive incoming updates using long polling.

        :param offset: Identifier of the first update to be returned.
        :param limit: Limits the number of updates to be retrieved.
            Values between 1—100 are accepted. Defaults to 100.
        :param timeout: Timeout in seconds for long polling.
            Defaults to 0, i.e. usual short polling. Should be positive,
            short polling should be used for testing purposes only.
        :param allowed_updates: List the types of updates you want your bot
            to receive.  For example, specify ['message',
            'edited_channel_post', 'callback_query'] to only receive updates
            of these types.
        :return: List of Update objects.

        """
        pass

    @_api_request(return_type=User)
    def get_me(self):
        """Returns basic information about the bot.

        :return: User.

        """
        pass

    @_api_request(return_type=Message)
    def send_message(self, *, chat_id, text, parse_mode=None,
                     disable_web_page_preview=None, disable_notification=None,
                     reply_to_message_id=None, reply_markup=None):
        """Use this method to send text messages.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param text: Text of the message to be sent.
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps
            to show bold, italic, fixed-width text or inline URLs in your
            bot's message.
        :param disable_web_page_preview: Disables link previews for links in
            this message.
        :param disable_notification: Sends the message silently. iOS users
            will not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def forward_message(self, *, chat_id, from_chat_id, message_id,
                        disable_notification=None):
        """Use this method to forward messages of any kind.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param from_chat_id: Unique identifier for the chat where the original
            message was sent (or channel username in the format
            @channelusername).
        :param message_id: Message identifier in the chat specified in
            from_chat_id.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_photo(self, *, chat_id, photo, caption=None,
                   disable_notification=None, reply_to_message_id=None,
                   reply_markup=None):
        """Use this method to send photos.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param photo: Photo to send. Pass a file_id as String to send a photo
            that exists on the Telegram servers (recommended), pass an HTTP URL
            as a String for Telegram to get a photo from the Internet, or
            upload a new photo.
        :param caption: Photo caption (may also be used when resending photos
            by file_id), 0-200 characters.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_audio(self, *, chat_id, audio, caption=None, duration=None,
                   performer=None, title=None, disable_notification=None,
                   reply_to_message_id=None, reply_markup=None):
        """Use this method to send audio files, if you want Telegram clients
        to display them in the music player. Your audio must be in the .mp3
        format.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param audio: Audio file to send. Pass a file_id as String to send an
            audio file that exists on the Telegram servers (recommended), pass
            an HTTP URL as a String for Telegram to get an audio file from the
            Internet, or upload a new.
        :param caption: Audio caption, 0-200 characters.
        :param duration: Duration of the audio in seconds.
        :param performer: Performer.
        :param title: Track name.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_document(self, *, chat_id, document, caption=None,
                      disable_notification=None, reply_to_message_id=None,
                      reply_markup=None):
        """Use this method to send general files.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param document: File to send. Pass a file_id as String to send a file
            that exists on the Telegram servers (recommended), pass an HTTP URL
            as a String for Telegram to get a file from the Internet, or upload
            a new.
        :param caption: Document caption (may also be used when resending
            documents by file_id), 0-200 characters.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_sticker(self, *, chat_id, sticker, disable_notification=None,
                     reply_to_message_id=None, reply_markup=None):
        """Use this method to send .webp stickers.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param sticker: Sticker to send. Pass a file_id as String to send a
            file that exists on the Telegram servers (recommended), pass an
            HTTP URL as a String for Telegram to get a .webp file from the
            Internet, or upload a new.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_video(self, *, chat_id, video, duration=None, width=None,
                   height=None, caption=None, disable_notification=None,
                   reply_to_message_id=None, reply_markup=None):
        """Use this method to send video files, Telegram clients support mp4
        videos (other formats may be sent as Document).

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param video: Video to send. Pass a file_id as String to send a video
            that exists on the Telegram servers (recommended), pass an HTTP URL
            as a String for Telegram to get a video from the Internet, or
            upload a new.
        :param duration: Duration of sent video in seconds.
        :param width: Video width.
        :param height: Video height.
        :param caption: Video caption (may also be used when resending videos
            by file_id), 0-200 characters.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return:
        """
        pass

    @_api_request(return_type=Message)
    def send_video_note(self, *, chat_id, video_note, duration=None,
                        length=None, disable_notification=None,
                        reply_to_message_id=None, reply_markup=None):
        """As of v.4.0, Telegram clients support rounded square mp4 videos of
        up to 1 minute long. Use this method to send video messages. On
        success, the sent Message is returned.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param video_note: Video note to send. Pass a file_id as String to send
            a video note that exists on the Telegram servers (recommended) or
            upload a new video.
        :param duration: Duration of sent video in seconds.
        :param length: Video width and height.
        :param disable_notification: Sends the message silently. Users will
            receive a notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_voice(self, *, chat_id, voice, caption=None, duration=None,
                   disable_notification=None, reply_to_message_id=None,
                   reply_markup=None):
        """Use this method to send audio files, if you want Telegram clients to
        display the file as a playable voice message. For this to work, your
        audio must be in an .ogg file encoded with OPUS (other formats may be
        sent as Audio or Document).

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param voice: Audio file to send. Pass a file_id as String to send a
            file that exists on the Telegram servers (recommended), pass an
            HTTP URL as a String for Telegram to get a file from the Internet,
            or upload a new.
        :param caption: Voice message caption, 0-200 characters.
        :param duration: Duration of the voice message in seconds.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_location(self, *, chat_id, latitude, longitude, live_period=None,
                      disable_notification=None, reply_to_message_id=None,
                      reply_markup=None):
        """Use this method to send point on the map.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param latitude: Latitude of location.
        :param longitude: Longitude of location.
        :param live_period: Period in seconds for which the location will be
            updated (see Live Locations, should be between 60 and 86400.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_venue(self, *, chat_id, latitude, longitude, title, address,
                   foursquare_id=None, disable_notification=None,
                   reply_to_message_id=None, reply_markup=None):
        """Use this method to send information about a venue.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param latitude: Latitude of the venue.
        :param longitude: Longitude of the venue.
        :param title: Name of the venue.
        :param address: Address of the venue.
        :param foursquare_id: Foursquare identifier of the venue.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def send_contact(self, *, chat_id, phone_number, first_name,
                     last_name=None, disable_notification=None,
                     reply_to_message_id=None, reply_markup=None):
        """Use this method to send phone contacts.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param phone_number: Contact's phone number.
        :param first_name: Contact's first name.
        :param last_name: Contact's last name.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: Additional interface options (
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove
            or ForceReply).
        :return: Message.

        """
        pass

    @_api_request()
    def send_chat_action(self, *, chat_id, action):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its
        typing status).

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param action: Type of action to broadcast. Choose one, depending on
            what the user is about to receive: typing for text messages,
            upload_photo for photos, record_video or upload_video for videos,
            record_audio or upload_audio for audio files, upload_document for
            general files, find_location for location data, record_video_note
            or upload_video_note for video notes.
        :return: True.

        """
        pass

    @_api_request(return_type=UserProfilePhotos)
    def get_user_profile_photos(self, *, user_id, offset=None, limit=None):
        """Use this method to get a list of profile pictures for a user.

        :param user_id: Unique identifier of the target user.
        :param offset: Sequential number of the first photo to be returned. By
            default, all photos are returned.
        :param limit: Limits the number of photos to be retrieved. Values
            between 1—100 are accepted. Defaults to 100.
        :return: UserProfilePhotos.

        """
        pass

    @_api_request(return_type=File)
    def get_file(self, *, file_id):
        """Use this method to get basic info about a file and prepare it for
            downloading.

        :param file_id: File identifier to get info about.
        :return: File.

        """
        pass

    @_api_request()
    def kick_chat_member(self, *, chat_id, user_id, until_date=None):
        """Use this method to kick a user from a group or a supergroup. In the
        case of supergroups, the user will not be able to return to the group
        on their own using invite links, etc., unless unbanned first. The bot
        must be an administrator in the group for this to work.

        :param chat_id: Unique identifier for the target group or username of
            the target supergroup (in the format @supergroupusername).
        :param user_id: Unique identifier of the target user.
        :param until_date: Date when the user will be unbanned, unix time. If
            user is banned for more than 366 days or less than 30 seconds from
            the current time they are considered to be banned forever.
        :return: True.

        """
        pass

    @_api_request()
    def leave_chat(self, *, chat_id):
        """Use this method for your bot to leave a group, supergroup or
            channel.

        :param chat_id: Unique identifier for the target group or username of
            the target supergroup (in the format @supergroupusername).
        :return: True.

        """
        pass

    @_api_request()
    def unban_chat_member(self, *, chat_id, user_id):
        """Use this method to unban a previously kicked user in a supergroup.
        The user will not return to the group automatically, but will be able
        to join via link, etc. The bot must be an administrator in the group
        for this to work.

        :param chat_id: Unique identifier for the target group or username of
            the target supergroup (in the format @supergroupusername).
        :param user_id: Unique identifier of the target user.
        :return: True.

        """
        pass

    @_api_request(return_type=Chat)
    def get_chat(self, *, chat_id):
        """Use this method to get up to date information about the chat
        (current name of the user for one-on-one conversations, current
        username of a user, group or channel, etc.).

        :param chat_id: Unique identifier for the target group or username of
            the target supergroup (in the format @supergroupusername).
        :return: Chat.

        """

        pass

    @_api_request(return_type=ChatMember)
    def get_chat_administrators(self, *, chat_id):
        """Use this method to get a list of administrators in a chat.

        :param chat_id: Unique identifier for the target chat or username of
            the target supergroup or channel (in the format @channelusername).
        :return: ChatMember.

        """
        pass

    @_api_request()
    def get_chat_members_count(self, *, chat_id):
        """Use this method to get the number of members in a chat.

        :param chat_id: Unique identifier for the target chat or username of
            the target supergroup or channel (in the format @channelusername).
        :return: int.

        """
        pass

    @_api_request(return_type=ChatMember)
    def get_chat_member(self, *, chat_id, user_id):
        """Use this method to get information about a member of a chat.

        :param chat_id: Unique identifier for the target chat or username of
            the target supergroup or channel (in the format @channelusername).
        :param user_id: Unique identifier of the target user.
        :return: ChatMember.

        """
        pass

    @_api_request()
    def answer_callback_query(self, *, callback_query_id, text=None, url=None,
                              show_alert=None, cache_time=None):
        """Use this method to send answers to callback queries sent from inline
        keyboards. The answer will be displayed to the user as a notification
        at the top of the chat screen or as an alert.

        :param callback_query_id: Unique identifier for the query to be
            answered.
        :param text: Text of the notification. If not specified, nothing will
            be shown to the user, 0-200 characters.
        :param url: URL that will be opened by the user's client. If you have
            created a Game and accepted the conditions via @Botfather, specify
            the URL that opens your game – note that this will only work if the
            query comes from a callback_game button.
        :param show_alert: If true, an alert will be shown by the client
            instead of a notification at the top of the chat screen. Defaults
            to false.
        :param cache_time: The maximum amount of time in seconds that the
            result of the callback query may be cached client-side. Telegram
            apps will support caching starting in version 3.14. Defaults to 0.
        :return: True.

        """
        pass

    @_api_request(return_type=Message)
    def edit_message_text(self, *, chat_id, text, message_id=None,
                          inline_message_id=None, parse_mode=None,
                          disable_web_page_preview=None, reply_markup=None):
        """Use this method to edit text and game messages sent by the bot or
        via the bot (for inline bots).

        :param chat_id:Required if inline_message_id is not specified. Unique
            identifier for the target chat or username of the target channel
            (in the format @channelusername).
        :param text: New text of the message.
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to
            show bold, italic, fixed-width text or inline URLs in your bot's
            message.
        :param disable_web_page_preview: Disables link previews for links in
            this message.
        :param reply_markup: InlineKeyboardMarkup.
        :return:  If edited message is sent by the bot, the edited Message is
            returned, otherwise True is returned.

        """
        pass

    @_api_request(return_type=Message)
    def edit_message_caption(self, *, chat_id=None, message_id=None,
                             inline_message_id=None, caption=None,
                             reply_markup=None):
        """Use this method to edit captions of messages sent by the bot or via
        the bot (for inline bots).

        :param chat_id: Required if inline_message_id is not specified. Unique
            identifier for the target chat or username of the target channel
            (in the format @channelusername).
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :param caption: New caption of the message.
        :param reply_markup: InlineKeyboardMarkup.
        :return: If edited message is sent by the bot, the edited Message is
            returned, otherwise True is returned.

        """
        pass

    @_api_request(return_type=Message)
    def edit_message_reply_markup(self, *, chat_id=None, message_id=None,
                                  inline_message_id=None, reply_markup=None):
        """Use this method to edit only the reply markup of messages sent by
        the bot or via the bot (for inline bots).

        :param chat_id: Required if inline_message_id is not specified. Unique
            identifier for the target chat or username of the target channel
            (in the format @channelusername).
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :param reply_markup: InlineKeyboardMarkup.
        :return:  If edited message is sent by the bot, the edited Message is
            returned, otherwise True is returned.

        """
        pass

    @_api_request(return_type=Message)
    def edit_message_live_location(self, *, latitude, longitude, chat_id=None,
                                   message_id=None, inline_message_id=None,
                                   reply_markup=None):
        """Use this method to edit live location messages sent by the bot or
        via the bot (for inline bots). A location can be edited until its
        live_period expires or editing is explicitly disabled by a call to
        stop_message_live_location. On success, if the edited message was sent
        by the bot, the edited Message is returned, otherwise True is returned.

        :param latitude: Latitude of new location.
        :param longitude: Longitude of new location.
        :param chat_id: Required if inline_message_id is not specified. Unique
            identifier for the target chat or username of the target channel
            (in the format @channelusername).
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :param reply_markup: A JSON-serialized object for a new inline
            keyboard.

        """
        pass

    @_api_request(return_type=Message)
    def stop_message_live_location(self, *, chat_id=None, message_id=None,
                                   inline_message_id=None, reply_markup=None):
        """Use this method to stop updating a live location message sent by the
        bot or via the bot (for inline bots) before live_period expires. On
        success, if the message was sent by the bot, the sent Message is
        returned, otherwise True is returned.

        :param chat_id: Required if inline_message_id is not specified. Unique
            identifier for the target chat or username of the target channel
            (in the format @channelusername).
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :param reply_markup: A JSON-serialized object for a new inline
            keyboard.

        """
        pass

    @_api_request()
    def delete_message(self, *, chat_id, message_id):
        """Use this method to delete a message, including service messages,
        with the following limitations:
            - A message can only be deleted if it was sent less than 48 hours
                ago.
            - Bots can delete outgoing messages in groups and supergroups.
            - Bots granted can_post_messages permissions can delete outgoing
                messages in channels.
            - If the bot is an administrator of a group, it can delete any
                message there.
            - If the bot has can_delete_messages permission in a supergroup or
                a channel, it can delete any message there.
        Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param message_id: Identifier of the message to delete.
        :return: True.

        """
        pass

    @_api_request()
    def answer_inline_query(self, *, inline_query_id, results,
                            cache_timer=None, is_personal=None,
                            next_offset=None, switch_pm_text=None,
                            switch_pm_parameter=None):
        """Use this method to send answers to an inline query.

        :param inline_query_id: Unique identifier for the answered query.
        :param results: List of results for the inline query.
        :param cache_timer: The maximum amount of time in seconds that the
            result of the inline query may be cached on the server. Defaults
            to 300.
        :param is_personal: Pass True, if results may be cached on the server
            side only for the user that sent the query. By default, results may
            be returned to any user who sends the same query.
        :param next_offset: Pass the offset that a client should send in the
            next query with the same text to receive more results. Pass an
            empty string if there are no more results or if you don‘t support
            pagination. Offset length can’t exceed 64 bytes.
        :param switch_pm_text: If passed, clients will display a button with
            specified text that switches the user to a private chat with the
            bot and sends the bot a start message with the parameter
            switch_pm_parameter.
        :param switch_pm_parameter: Deep-linking parameter for the /start
            message sent to the bot when user presses the switch button.
            1-64 characters, only A-Z, a-z, 0-9, _ and - are allowed.
        :return: True.

        """
        pass

    @_api_request(return_type=Message)
    def send_game(self, *, chat_id, game_short_name, disable_notification=None,
                  reply_to_message_id=None, reply_markup=None):
        """Use this method to send a game.

        :param chat_id: Unique identifier for the target chat.
        :param game_short_name: Short name of the game, serves as the unique
            identifier for the game. Set up your games via Botfather.
        :param disable_notification: Sends the message silently. iOS users will
            not receive a notification, Android users will receive a
            notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: InlineKeyboardMarkup.
        :return: Message.

        """
        pass

    @_api_request(return_type=Message)
    def set_game_score(self, *, user_id, score, force=None,
                       disable_edit_message=None, chat_id=None,
                       message_id=None, inline_message_id=None):
        """Use this method to set the score of the specified user in a game.

        :param user_id: User identifier.
        :param score: New score, must be non-negative.
        :param force: Pass True, if the high score is allowed to decrease.
            This can be useful when fixing mistakes or banning cheaters.
        :param disable_edit_message: Pass True, if the game message should not
            be automatically edited to include the current scoreboard.
        :param chat_id: Required if inline_message_id is not specified. Unique
            identifier for the target chat.
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :return: if the message was sent by the bot, returns the edited
            Message, otherwise returns True. Returns an error, if the new score
            is not greater than the user's current score in the chat and force
            is False.

        """
        pass

    @_api_request(return_type=GameHighScore)
    def get_game_high_scores(self, *, user_id, chat_id=None, message_id=None,
                             inline_message_id=None):
        """Use this method to get data for high score tables.

        :param user_id: Target user id.
        :param chat_id: Required if inline_message_id is not specified. Unique
            identifier for the target chat.
        :param message_id: Required if inline_message_id is not specified.
            Identifier of the sent message.
        :param inline_message_id: Required if chat_id and message_id are not
            specified. Identifier of the inline message.
        :return: List of GameHighScore.

        """
        pass

    @_api_request(return_type=Message)
    def send_invoice(self, *, chat_id, title, payload, provider_token, prices,
                     start_parameter, currency, photo_url=None, need_name=None,
                     description=None, photo_size=None, photo_width=None,
                     photo_height=None, need_phone_number=None,
                     need_email=None, need_shipping_address=None,
                     is_flexible=None, disable_notification=None,
                     reply_to_message_id=None, reply_markup=None):
        """Use this method to send invoices.

        :param chat_id: Unique identifier for the target private chat.
        :param title: Product name, 1-32 characters.
        :param payload: Bot-defined invoice payload, 1-128 bytes. This will not
            be displayed to the user, use for your internal processes.
        :param provider_token: Payments provider token, obtained via Botfather.
        :param prices: List of LabeledPrice. Price breakdown, a list of
            components (e.g. product price, tax, discount, delivery cost,
            delivery tax, bonus, etc.).
        :param start_parameter: Unique deep-linking parameter that can be used
            to generate this invoice when used as a start parameter.
        :param currency: Three-letter ISO 4217 currency code.
        :param photo_url: URL of the product photo for the invoice. Can be a
            photo of the goods or a marketing image for a service. People like
            it better when they see what they are paying for.
        :param need_name: Pass True, if you require the user's full name to
            complete the order.
        :param description: Product description, 1-255 characters.
        :param photo_size: Photo size.
        :param photo_width: Photo width.
        :param photo_height: Photo height.
        :param need_phone_number: Pass True, if you require the user's phone
            number to complete the order.
        :param need_email: Pass True, if you require the user's email to
            complete the order.
        :param need_shipping_address: Pass True, if you require the user's
            shipping address to complete the order.
        :param is_flexible: Pass True, if the final price depends on the
            shipping method.
        :param disable_notification: Sends the message silently. Users will
            receive a notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the
            original message.
        :param reply_markup: InlineKeyboardMarkup.
        :return: Message.

        """
        pass

    @_api_request()
    def answer_shipping_query(self, shipping_query_id, ok,
                              shipping_options=None, error_message=None):
        """If you sent an invoice requesting a shipping address and the
        parameter is_flexible was specified, the Bot API will send an Update
        with a shipping_query field to the bot. Use this method to reply to
        shipping queries. On success, True is returned.

        :param shipping_query_id: Unique identifier for the query to be
            answered.
        :param ok: Specify True if delivery to the specified address is
            possible and False if there are any problems (for example, if
            delivery to the specified address is not possible).
        :param shipping_options: List of ShippingOption. Required if ok is
            True.
        :param error_message: Required if ok is False. Error message in human
            readable form that explains why it is impossible to complete the
            order (e.g. "Sorry, delivery to your desired address is
            unavailable'). Telegram will display this message to the user.
        :return: True.

        """
        pass

    @_api_request()
    def answer_pre_checkout_query(self, pre_checkout_query_id, ok,
                                  error_message=None):
        """Once the user has confirmed their payment and shipping details,
        the Bot API sends the final confirmation in the form of an Update with
        the field pre_checkout_query. Use this method to respond to such
        pre-checkout queries. On success, True is returned. Note: The Bot API
        must receive an answer within 10 seconds after the pre-checkout query
        was sent.

        :param pre_checkout_query_id: Unique identifier for the query to be
            answered.
        :param ok: Specify True if everything is alright (goods are available,
            etc.) and the bot is ready to proceed with the order. Use False if
            there are any problems.
        :param error_message: Required if ok is False. Error message in human
            readable form that explains the reason for failure to proceed with
            the checkout (e.g. "Sorry, somebody just bought the last of our
            amazing black T-shirts while you were busy filling out your payment
            details. Please choose a different color or garment!"). Telegram
            will display this message to the user.
        :return: True.

        """
        pass

    @_api_request()
    def restrict_chat_member(self, *, chat_id, user_id, until_date=None,
                             can_send_messages=None,
                             can_send_media_messages=None,
                             can_send_other_messages=None,
                             can_add_web_page_previews=None):
        """Use this method to restrict a user in a supergroup. The bot must be
        an administrator in the supergroup for this to work and must have the
        appropriate admin rights. Pass True for all boolean parameters to lift
        restrictions from a user. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target supergroup (in the format @supergroupusername).
        :param user_id: Unique identifier of the target user.
        :param until_date: Date when restrictions will be lifted for the user,
            unix time. If user is restricted for more than 366 days or less
            than 30 seconds from the current time, they are considered to be
            restricted forever.
        :param can_send_messages: Pass True, if the user can send text
            messages, contacts, locations and venues.
        :param can_send_media_messages: Pass True, if the user can send audios,
            documents, photos, videos, video notes and voice notes, implies
            can_send_messages.
        :param can_send_other_messages: Pass True, if the user can send
            animations, games, stickers and use inline bots, implies
            can_send_media_messages.
        :param can_add_web_page_previews: Pass True, if the user may add web
            page previews to their messages, implies can_send_media_messages.
        :return: True.

        """
        pass

    @_api_request()
    def promote_chat_member(self, *, chat_id, user_id, can_change_info=None,
                            can_post_messages=None, can_edit_messages=None,
                            can_delete_messages=None, can_invite_users=None,
                            can_restrict_members=None, can_pin_messages=None,
                            can_promote_members=None):
        """se this method to promote or demote a user in a supergroup or a
        channel. The bot must be an administrator in the chat for this to work
        and must have the appropriate admin rights. Pass False for all boolean
        parameters to demote a user. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param user_id: Unique identifier of the target user.
        :param can_change_info: Pass True, if the administrator can change chat
            title, photo and other settings.
        :param can_post_messages: Pass True, if the administrator can create
            channel posts, channels only.
        :param can_edit_messages: Pass True, if the administrator can edit
            messages of other users, channels only.
        :param can_delete_messages: Pass True, if the administrator can delete
            messages of other users.
        :param can_invite_users: Pass True, if the administrator can invite new
            users to the chat.
        :param can_restrict_members: Pass True, if the administrator can
            restrict, ban or unban chat members.
        :param can_pin_messages: Pass True, if the administrator can pin
            messages, supergroups only.
        :param can_promote_members: Pass True, if the administrator can add new
            administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly
            (promoted by administrators that were appointed by him).
        :return: True.

        """
        pass

    @_api_request()
    def export_chat_invite_link(self, *, chat_id):
        """Use this method to export an invite link to a supergroup or a
        channel. The bot must be an administrator in the chat for this to work
        and must have the appropriate admin rights. Returns exported invite
        link as String on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :return: str.

        """
        pass

    @_api_request()
    def set_chat_photo(self, *, chat_id, photo):
        """Use this method to set a new profile photo for the chat. Photos
        can't be changed for private chats. The bot must be an administrator in
        the chat for this to work and must have the appropriate admin rights.
        Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param photo: Image file.
        :return: True.

        """
        pass

    @_api_request()
    def set_chat_sticker_set(self, *, chat_id, sticker_set_name):
        """Use this method to set a new group sticker set for a supergroup.
        The bot must be an administrator in the chat for this to work and must
        have the appropriate admin rights. Use the field can_set_sticker_set
        optionally returned in getChat requests to check if the bot can use
        this method. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target supergroup (in the format @supergroupusername).
        :param sticker_set_name: Name of the sticker set to be set as the group
            sticker set.

        """
        pass

    @_api_request()
    def delete_chat_sticker_set(self, *, chat_id):
        """Use this method to delete a group sticker set from a supergroup.
        The bot must be an administrator in the chat for this to work and must
        have the appropriate admin rights. Use the field can_set_sticker_set
        optionally returned in getChat requests to check if the bot can use
        this method. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target supergroup (in the format @supergroupusername).

        """
        pass

    @_api_request()
    def delete_chat_photo(self, *, chat_id):
        """Use this method to delete a chat photo. Photos can't be changed for
        private chats. The bot must be an administrator in the chat for this to
        work and must have the appropriate admin rights.
        Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :return: True.

        """
        pass

    @_api_request()
    def set_chat_title(self, *, chat_id, title):
        """Use this method to change the title of a chat. Titles can't be
        changed for private chats. The bot must be an administrator in the chat
        for this to work and must have the appropriate admin rights.
        Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param title: New chat title, 1-255 characters.
        :return: True.

        """
        pass

    @_api_request()
    def set_chat_description(self, *, chat_id, description=None):
        """Use this method to change the description of a supergroup or a
        channel. The bot must be an administrator in the chat for this to work
        and must have the appropriate admin rights. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param description: New chat description, 0-255 characters.
        :return: True.

        """
        pass

    @_api_request()
    def pin_chat_message(self, *, chat_id, message_id,
                         disable_notification=None):
        """Use this method to pin a message in a supergroup. The bot must be an
        administrator in the chat for this to work and must have the
        appropriate admin rights. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :param message_id: Identifier of a message to pin.
        :param disable_notification: Pass True, if it is not necessary to send
            a notification to all group members about the new pinned message.
        :return: True

        """
        pass

    @_api_request()
    def unpin_chat_message(self, *, chat_id):
        """Use this method to unpin a message in a supergroup chat. The bot
        must be an administrator in the chat for this to work and must have the
        appropriate admin rights. Returns True on success.

        :param chat_id: Unique identifier for the target chat or username of
            the target channel (in the format @channelusername).
        :return: True.

        """
        pass

    @_api_request(return_type=StickerSet)
    def get_sticker_set(self, *, name):
        """Use this method to get a sticker set. On success, a StickerSet
        object is returned.

        :param name: Name of the sticker set.
        :return: StickerSet.

        """
        pass

    @_api_request(return_type=File)
    def upload_sticker_file(self, *, user_id, png_sticker):
        """Use this method to upload a .png file with a sticker for later use
        in create_new_sticker_set and add_sticker_to_set methods (can be used
        multiple times). Returns the uploaded File on success.

        :param user_id: User identifier of sticker file owner.
        :param png_sticker: PNG image with the sticker, must be up to 512
            kilobytes in size, dimensions must not exceed 512px, and either
            width or height must be exactly 512px.

        """
        pass

    @_api_request()
    def create_new_sticker_set(self, *, user_id, name, title, png_sticker,
                               emojis, contains_masks=None,
                               mask_position=None):
        """Use this method to create new sticker set owned by a user. The bot
        will be able to edit the created sticker set. Returns True on success.

        :param user_id: User identifier of created sticker set owner.
        :param name: Short name of sticker set, to be used in t.me/addstickers/
            URLs (e.g., animals). Can contain only english letters, digits and
            underscores. Must begin with a letter, can't contain consecutive
            underscores and must end in “_by_<bot username>”. <bot_username> is
            case insensitive. 1-64 characters.
        :param title: Sticker set title, 1-64 characters.
        :param png_sticker: Png image with the sticker, must be up to 512
            kilobytes in size, dimensions must not exceed 512px, and either
            width or height must be exactly 512px. Pass a file_id as a string
            to send a file that already exists on the Telegram servers, pass an
            HTTP URL as a string for Telegram to get a file from the Internet,
            or upload a new one using multipart/form-data.
        :param emojis: One or more emoji corresponding to the sticker.
        :param contains_masks: Pass True, if a set of mask stickers should be
            created.
        :param mask_position: MaskPosition instance.

        """
        pass

    @_api_request()
    def add_sticker_to_set(self, *, user_id, name, png_sticker, emojis,
                           mask_position=None):
        """Use this method to add a new sticker to a set created by the bot.
        Returns True on success.

        :param user_id: User identifier of sticker set owner.
        :param name: Sticker set name.
        :param png_sticker: PNG image with the sticker, must be up to 512
            kilobytes in size, dimensions must not exceed 512px, and either
            width or height must be exactly 512px. Pass a file_id as a string
            to send a file that already exists on the Telegram servers, pass an
            HTTP URL as a string for Telegram to get a file from the Internet,
            or upload a new one using multipart/form-data.
        :param emojis: One or more emoji corresponding to the sticker.
        :param mask_position: MaskPosition instance.

        """
        pass

    @_api_request()
    def set_sticker_position_in_set(self, *, sticker, position):
        """Use this method to move a sticker in a set created by the bot to a
        specific position . Returns True on success.

        :param sticker: File identifier of the sticker.
        :param position: New sticker position in the set, zero-based.

        """
        pass

    @_api_request()
    def delete_sticker_from_set(self, *, sticker):
        """Use this method to delete a sticker from a set created by the bot.
        Returns True on success.

        :param sticker: File identifier of the sticker.

        """
        pass

    @_api_request(return_type=Chat)
    def get_chat(self, *, chat_id):
        """Use this method to get up to date information about the chat
        (current name of the user for one-on-one conversations, current
        username of a user, group or channel, etc.). Returns a Chat object on
        success.

        :param chat_id: Unique identifier for the target chat or username of t
        he target supergroup or channel (in the format @channelusername)

        """
        pass
