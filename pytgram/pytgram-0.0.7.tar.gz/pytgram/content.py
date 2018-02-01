"""content module.

This module describes the incoming content.

"""


from functools import wraps

from .url import get_url


def _replace_args(*args):
    """Class decorator. Changes built-in names in kwargs.

    :param args: arg names (id, from, type).

    """
    def wrapper(cls):
        origin_init = cls.__init__

        @wraps(cls.__init__)
        def __init__(self, **kwargs):
            replace_dict = {arg + '_': kwargs.pop(arg) for arg in args}
            kwargs.update(replace_dict)
            origin_init(self, **kwargs)

        cls.__init__ = __init__
        return cls
    return wrapper


class _Content(object):
    """Base class."""

    @classmethod
    def from_list(cls, dict_list):
        return [cls(**obj_dict) for obj_dict in dict_list]


class DictItem(object):
    """Base class."""

    def to_dict(self):
        args_dict = {key: val for key, val in self.__dict__.items() if val}
        return args_dict


class _Query(_Content):
    """Base class for query types."""

    def get_str_type(self):
        """Makes a string from the class name by separating the case."""

        str_type = ''
        for char in self.__class__.__name__:
            if char.isupper():
                str_type += '_{}'.format(char.lower())
            else:
                str_type += char
        return str_type[1:]


class _MediaContent(_Content):
    """Base class for media content."""

    def __init__(self, file_id, file_size=None, **kwargs):
        self.id = file_id
        self.size = file_size

        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def __str__(self):
        return '{}(id{})'.format(self.__class__.__name__, self.id)


class Update(_Content):
    """This class represents an incoming update. """

    def __init__(self, update_id, message=None, edited_message=None,
                 channel_post=None, edited_channel_post=None,
                 inline_query=None, chosen_inline_result=None,
                 callback_query=None, shipping_query=None,
                 pre_checkout_query=None):
        """Initial instance.

        :param update_id: The update‘s unique identifier. Update identifiers
            start from a certain positive number and increase sequentially.
            This ID becomes especially handy if you’re using Webhooks, since it
            allows you to ignore repeated updates or to restore the correct
            update sequence, should they get out of order.
        :param message: New incoming message of any kind — text, photo,
            sticker, etc.
        :param edited_message: New version of a message that is known to the
            bot and was edited.
        :param channel_post: New incoming channel post of any kind — text,
            photo, sticker, etc.
        :param edited_channel_post: New version of a channel post that is known
            to the bot and was edited.
        :param inline_query: New incoming inline query.
        :param chosen_inline_result: The result of an inline query that was
            chosen by a user and sent to their chat partner.
        :param callback_query: New incoming callback query.
        :param shipping_query: New incoming shipping query. Only for invoices
            with flexible price.
        :param pre_checkout_query: New incoming pre-checkout query. Contains
            full information about checkout.

        """
        self.id = update_id
        message_dict = (
            message or edited_message or channel_post or edited_channel_post
        )
        if message_dict:
            self.content = Message(**message_dict)
        if inline_query:
            self.content = InlineQuery(**inline_query)
        if chosen_inline_result:
            self.content = ChosenInlineResult(**chosen_inline_result)
        if callback_query:
            self.content = CallbackQuery(**callback_query)
        if shipping_query:
            self.content = ShippingQuery(**shipping_query)
        if pre_checkout_query:
            self.content = PreCheckoutQuery(**pre_checkout_query)

    def __str__(self):
        return '{}(id:{id}, content:{content})'.format(self.__class__.__name__,
                                                       **self.__dict__)


@_replace_args('id')
class User(_Content):
    """This class represents a Telegram user or bot."""

    def __init__(self, id_, first_name, last_name=None, username=None,
                 language_code=None, is_bot=None):
        """Initial instance.

        :param id_: Unique identifier for this user or bot.
        :param first_name: User‘s or bot’s first name.
        :param last_name: User‘s or bot’s last name.
        :param username: User‘s or bot’s username.
        :param language_code: IETF language tag of the user's language.
        :param is_bot: True, if this user is a bot.

        """
        self.id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.is_bot = is_bot

    def __str__(self):
        return '{}(id:{id}, username:{username})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


@_replace_args('type')
class Chat(User):
    """This class represents a chat."""

    def __init__(self, type_, all_members_are_administrators=None, title=None,
                 photo=None, description=None, invite_link=None,
                 pinned_message=None, **kwargs):
        """Initial instance.

        :param type_: Type of chat, can be either 'private', 'group',
            'supergroup' or 'channel'.
        :param all_members_are_administrators: True if a group has
            'All Members Are Admins' enabled.
        :param title: Title, for supergroups, channels and group chats.
        :param photo: ChatPhoto. Returned only in get_chat.
        :param description: Description, for supergroups and channel chats.
            Returned only in get_chat.
        :param invite_link: Chat invite link, for supergroups and channel
            chats. Returned only in get_chat.
        :param pinned_message: Pinned message, for supergroups and channel
            chats. Returned only in get_chat.
        :param kwargs: id, username, first_name, last_name.

        """
        super(Chat, self).__init__(**kwargs)
        self.type = type_
        self.title = title
        self.description = description
        self.invite_link = invite_link
        if pinned_message:
            self.pinned_message = Message(**pinned_message)
        if photo:
            self.photo = ChatPhoto(**photo)
        self.all_members_are_administrators = all_members_are_administrators

    def __str__(self):
        return '{}(id:{id}, type:{type})'.format(self.__class__.__name__,
                                                 **self.__dict__)


class ChatPhoto(_Content):
    """This class represents a chat photo."""

    def __init__(self, small_file_id, big_file_id):
        """Initial instance.

        :param small_file_id: Unique file identifier of small (160x160) chat
            photo. This file_id can be used only for photo download.
        :param big_file_id: Unique file identifier of big (640x640) chat photo.
            This file_id can be used only for photo download.

        """
        self.small_file_id = small_file_id
        self.big_file_id = big_file_id


class Contact(User):
    """This class represents a phone contact."""

    def __init__(self, phone_number, **kwargs):
        """Initial instance.

        :param phone_number: Contact's phone number.
        :param kwargs: user_id, first_name, last_name.

        """
        kwargs['id'] = kwargs.pop('user_id', None)
        super(Contact, self).__init__(**kwargs)
        self.phone_number = phone_number

    def __str__(self):
        return '{}(id:{id}, phone_number:{phone_number})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


@_replace_args('from')
class Message(_Content):
    """This class represents a message."""

    def __init__(self, message_id, date, chat, from_=None, forward_from=None,
                 forward_from_chat=None, forward_from_message_id=None,
                 forward_date=None, reply_to_message=None, edit_date=None,
                 text=None, entities=None, audio=None, document=None,
                 game=None, photo=None, sticker=None, video=None, voice=None,
                 caption=None, contact=None, location=None, venue=None,
                 new_chat_members=None, left_chat_member=None, video_note=None,
                 new_chat_title=None, new_chat_photo=None,
                 delete_chat_photo=None, group_chat_created=None,
                 channel_chat_created=None, migrate_to_chat_id=None,
                 migrate_from_chat_id=None, pinned_message=None, invoice=None,
                 successful_payment=None, author_signature=None,
                 forward_signature=None, caption_entities=None):
        """Initial instance.

        :param message_id: Unique message identifier inside this chat.
        :param date: Date the message was sent in Unix time.
        :param chat: Conversation the message belongs to.
        :param from_: Sender, can be empty for messages sent to channels.
        :param forward_from: For forwarded messages, sender of the original
            message.
        :param forward_from_chat: For messages forwarded from a channel,
            information about the original channel.
        :param forward_from_message_id: For forwarded channel posts, identifier
            of the original message in the channel.
        :param forward_date: For forwarded messages, date the original message
            was sent in Unix time.
        :param reply_to_message: For replies, the original message. Note that
            the Message object in this field will not contain further
            reply_to_message fields even if it itself is a reply.
        :param edit_date: Date the message was last edited in Unix time.
        :param text: For text messages, the actual UTF-8 text of the message,
            0-4096 characters.
        :param entities: For text messages, special entities like usernames,
            URLs, bot commands, etc. that appear in the text.
        :param audio: Message is an audio file, information about the file.
        :param document: Message is a general file, information about the file.
        :param game: Message is a game, information about the game.
        :param photo: Message is a photo, available sizes of the photo.
        :param sticker: Message is a sticker, information about the sticker.
        :param video: Message is a video, information about the video.
        :param video_note: Message is a video note, information about the video
            message.
        :param voice: Message is a voice message, information about the file.
        :param caption: Caption for the document, photo or video, 0-200
            characters.
        :param contact: Message is a shared contact, information about the
            contact.
        :param location: Message is a shared location, information about the
            location.
        :param venue: Message is a venue, information about the venue.
        :param new_chat_members:  New members that were added to the group or
            supergroup and information about them (the bot itself may be one of
            these members).
        :param left_chat_member: A member was removed from the group,
            information about them (this member may be the bot itself).
        :param new_chat_title: A chat title was changed to this value.
        :param new_chat_photo: A chat photo was change to this value.
        :param delete_chat_photo: Service message: the chat photo was deleted.
        :param group_chat_created: Service message: the group has been created.
        :param channel_chat_created: Service message: the channel has been
            created. This field can‘t be received in a message coming through
            updates, because bot can’t be a member of a channel when it is
            created. It can only be found in reply_to_message if someone
            replies to a very first message in a channel.
        :param migrate_to_chat_id: The group has been migrated to a supergroup
            with the specified identifier. This number may be greater than 32
            bits and some programming languages may have difficulty/silent
            defects in interpreting it. But it is smaller than 52 bits, so a
            signed 64 bit integer or double-precision float type are safe for
            storing this identifier.
        :param migrate_from_chat_id: The supergroup has been migrated from a
            group with the specified identifier. This number may be greater
            than 32 bits and some programming languages may have
            difficulty/silent defects in interpreting it. But it is smaller
            than 52 bits, so a signed 64 bit integer or double-precision
            float type are safe for storing this identifier.
        :param pinned_message: Specified message was pinned. Note that the
            Message object in this field will not contain further
            reply_to_message fields even if it is itself a reply.
        :param invoice: Message is an invoice for a payment, information about
            the invoice.
        :param successful_payment:  Message is a service message about a
            successful payment, information about the payment.
        :param author_signature: Signature of the post author for messages in
            channels.
        :param forward_signature: For messages forwarded from channels,
            signature of the post author if present.
        :param caption_entities: For messages with a caption, special entities
            like usernames, URLs, bot commands, etc. that appear in the
            caption.

        """
        self.id = message_id
        self.date = date
        self.chat = Chat(**chat)
        self.content_type = None
        self.delete_chat_photo = delete_chat_photo
        self.forward_from_message_id = forward_from_message_id
        self.forward_date = forward_date
        self.edit_date = edit_date
        self.caption = caption
        self.new_chat_title = new_chat_title
        self.group_chat_created = group_chat_created
        self.channel_chat_created = channel_chat_created
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.author_signature = author_signature
        self.forward_signature = forward_signature
        if from_:
            self.from_user = User(**from_)
        if forward_from:
            self.forward_from = User(**forward_from)
        if forward_from_chat:
            self.forward_from_chat = Chat(**forward_from_chat)
        if reply_to_message:
            self.reply_to_message = Message(**reply_to_message)
        if entities:
            self.entities = MessageEntity.from_list(entities)
        if audio:
            self.audio = Audio(**audio)
            self.content_type = 'audio'
        if document:
            self.document = Document(**document)
            self.content_type = 'document'
        if photo:
            self.photo = PhotoSize.from_list(photo)
            self.content_type = 'photo'
        if game:
            self.game = Game(**game)
            self.content_type = 'game'
        if sticker:
            self.sticker = Sticker(**sticker)
            self.content_type = 'sticker'
        if video:
            self.video = Video(**video)
            self.content_type = 'video'
        if video_note:
            self.video_note = VideoNote(**video_note)
            self.content_type = 'video_note'
        if voice:
            self.voice = Voice(**voice)
            self.content_type = 'voice'
        if contact:
            self.contact = Contact(**contact)
            self.content_type = 'contact'
        if location:
            self.location = Location(**location)
            self.content_type = 'location'
        if venue:
            self.venue = Venue(**venue)
            self.content_type = 'venue'
        if text:
            self.text = text
            self.content_type = 'text'
        if invoice:
            self.invoice = Invoice(**invoice)
            self.content_type = 'invoice'
        if successful_payment:
            self.successful_payment = SuccessfulPayment(**successful_payment)
            self.content_type = 'successful_payment'
        if new_chat_members:
            self.new_chat_members = User.from_list(new_chat_members)
        if left_chat_member:
            self.left_chat_member = User(**left_chat_member)
        if new_chat_photo:
            self.new_chat_photo = PhotoSize.from_list(new_chat_photo)
        if pinned_message:
            self.pinned_message = Message(**pinned_message)
        if caption_entities:
            self.caption_entities = MessageEntity.from_list(caption_entities)

    def __str__(self):
        return '{}(id:{id}, from:{from_user}, ' \
               'content_type:{content_type})'.format(self.__class__.__name__,
                                                     **self.__dict__)


@_replace_args('type')
class MessageEntity(_Content):
    """This class represents one special entity in a text message.
    For example, hashtags, usernames, URLs, etc.

    """
    def __init__(self, type_, offset, length, url=None, user=None):
        """Initial instance.

        :param type_: Type of the entity. Can be mention (@username), hashtag,
            bot_command, url, email, bold (bold text), italic (italic text),
            code (monowidth string), pre (monowidth block), text_link (for
            clickable text URLs), text_mention (for users without usernames).
        :param offset: Offset in UTF-16 code units to the start of the entity.
        :param length: Length of the entity in UTF-16 code units.
        :param url: For “text_link” only, url that will be opened after user
            taps on the text.
        :param user: For 'text_mention' only, the mentioned user.

        """
        self.type = type_
        self.offset = offset
        self.length = length
        self.url = url
        self.user = user

    def __str__(self):
        return '{}(type:{})'.format(self.__class__.__name__, self.type)


class PhotoSize(_MediaContent):
    """This class represents one size of a photo or a file / sticker
    thumbnail.

    """
    pass


class Audio(_MediaContent):
    """This class represents an audio file to be treated as music by the
    Telegram clients.

    """
    def __init__(self, performer=None, title=None, **kwargs):
        """Initial instance.

        :param performer: Performer of the audio as defined by sender or by
            audio tags.
        :param title: Title of the audio as defined by sender or by audio tags.
        :param kwargs: file_id, duration, mime_type, file_size.

        """
        super(Audio, self).__init__(**kwargs)
        self.performer = performer
        self.title = title


class Document(_MediaContent):
    """This class represents a general file (as opposed to photos, voice
    messages and audio files).

    """
    def __init__(self, file_name=None, **kwargs):
        """Initial instance.

        :param file_name: Original filename as defined by sender.
        :param kwargs: file_id, thumb, mime_type, file_size.

        """
        super(Document, self).__init__(**kwargs)
        self.file_name = file_name


class Sticker(_MediaContent):
    """This class represents a sticker."""

    def __init__(self, emoji=None, set_name=None, mask_position=None,
                 **kwargs):
        """Initial instance.

        :param emoji: Emoji associated with the sticker.
        :param set_name: Name of the sticker set to which the sticker belongs.
        :param mask_position: For mask stickers, the position where the mask
            should be placed.
        :param kwargs: file_id, width, height, thumb, file_size.

        """
        super(Sticker, self).__init__(**kwargs)
        self.emoji = emoji
        self.set_name = set_name
        if mask_position:
            self.mask_position = MaskPosition(**mask_position)


class MaskPosition(DictItem):
    """This class describes the position on faces where a mask should be placed
    by default.

    """
    def __init__(self, point, x_shift, y_shift, scale):
        """Initial instance.

        :param point: The part of the face relative to which the mask should be
            placed. One of "forehead", "eyes", "mouth", or "chin".
        :param x_shift: Shift by X-axis measured in widths of the mask scaled
            to the face size, from left to right. For example, choosing -1.0
            will place mask just to the left of the default mask position.
        :param y_shift: Shift by Y-axis measured in heights of the mask scaled
            to the face size, from top to bottom. For example, 1.0 will place
            the mask just below the default mask position.
        :param scale: Mask scaling coefficient. For example, 2.0 means double
            size.

        """
        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.scale = scale


class StickerSet(_Content):
    """This class represents a sticker set."""

    def __init__(self, name, title, contains_masks, stickers):
        """Initial instance.

        :param name: Sticker set name.
        :param title: Sticker set title.
        :param contains_masks: True, if the sticker set contains masks.
        :param stickers: List of Sticker.

        """
        self.name = name
        self.title = title
        self.contains_masks = contains_masks
        if stickers:
            self.stickers = Sticker.from_list(stickers)


class Video(_MediaContent):
    """This class represents a video file."""
    pass


class VideoNote(_MediaContent):
    pass


class Voice(_MediaContent):
    """This class represents a voice note."""
    pass


class File(_MediaContent):
    """This class represents a file ready to be downloaded."""

    def __init__(self, file_path=None, **kwargs):
        """Initial instance.

        :param file_path: File path.
        :param kwargs: file_id, file_size.

        """
        super(File, self).__init__(**kwargs)
        if file_path:
            self.url = get_url(url_type='file', token='{token}',
                               path=file_path)


class Location(_Content):
    """This class represents a point on the map."""

    def __init__(self, longitude, latitude):
        """Initial instance.

        :param longitude: Longitude as defined by sender.
        :param latitude: Latitude as defined by sender.

        """
        self.longitude = longitude
        self.latitude = latitude

    def __str__(self):
        return '{}(latitude:{latitude}, longitude:{longitude})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


class Venue(_Content):
    """This class represents a venue."""

    def __init__(self, location, title, address, foursquare_id=None):
        """Initial instance.

        :param location: Venue location.
        :param title: Name of the venue.
        :param address: Address of the venue.
        :param foursquare_id: Foursquare identifier of the venue.

        """
        self.location = Location(**location)
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id

    def __str__(self):
        return '{}(location:{location}, title:{title}, ' \
               'address:{address})'.format(self.__class__.__name__,
                                           **self.__dict__)


class UserProfilePhotos(_Content):
    """This class represent a user's profile pictures."""

    def __init__(self, total_count, photos):
        """Initial instance.

        :param total_count: Total number of profile pictures the target user
            has.
        :param photos: Requested profile pictures (in up to 4 sizes each).

        """
        self.total_count = total_count
        self.photos = [PhotoSize.from_list(p_list) for p_list in photos]

    def __iter__(self):
        for photo_list in self.photos:
            yield photo_list

    def __str__(self):
        return '{}(photos:{})'.format(self.__class__.__name__, self.photos)


class ChatMember(_Content):
    """This class contains information about one member of the chat."""

    def __init__(self, user, status, until_date=None, can_be_edited=None,
                 can_change_info=None, can_post_messages=None,
                 can_edit_messages=None, can_delete_messages=None,
                 can_invite_users=None, can_restrict_members=None,
                 can_pin_messages=None, can_promote_members=None,
                 can_send_messages=None, can_send_media_messages=None,
                 can_send_other_messages=None, can_add_web_page_previews=None):
        """Initial instance.

        :param user: Information about the user.
        :param status: The member's status in the chat. Can be 'creator',
            'administrator', 'member', 'left' or 'kicked'.
        :param until_date: Restictred and kicked only. Date when restrictions
            will be lifted for this user, unix time.
        :param can_be_edited: Administrators only. True, if the bot is allowed
            to edit administrator privileges of that user.
        :param can_change_info: Administrators only. True, if the administrator
            can change the chat title, photo and other settings.
        :param can_post_messages: Administrators only. True, if the
            administrator can post in the channel, channels only.
        :param can_edit_messages: Administrators only. True, if the
            administrator can edit messages of other users, channels only.
        :param can_delete_messages: Administrators only. True, if the
            administrator can delete messages of other users.
        :param can_invite_users: Administrators only. True, if the
            administrator can invite new users to the chat.
        :param can_restrict_members: Administrators only. True, if the
            administrator can restrict, ban or unban chat members.
        :param can_pin_messages: Administrators only. True, if the
            administrator can pin messages, supergroups only.
        :param can_promote_members: Administrators only. True, if the
            administrator can add new administrators with a subset of his own
            privileges or demote administrators that he has promoted, directly
            or indirectly (promoted by administrators that were appointed by
            the user).
        :param can_send_messages: Restricted only. True, if the user can send
            text messages, contacts, locations and venues.
        :param can_send_media_messages: Restricted only. True, if the user can
            send audios, documents, photos, videos, video notes and voice
            notes, implies can_send_messages.
        :param can_send_other_messages: Restricted only. True, if the user can
            send animations, games, stickers and use inline bots, implies
            can_send_media_messages.
        :param can_add_web_page_previews: Restricted only. True, if user may
            add web page previews to his messages, implies
            can_send_media_messages.

        """
        self.user = User(**user)
        self.status = status
        self.until_date = until_date
        self.can_be_edited = can_be_edited
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews

    def __str__(self):
        return '{}(user:{user}, status:{status})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


@_replace_args('id', 'from')
class InlineQuery(_Query):
    """This class represents an incoming inline query."""

    def __init__(self, id_, from_, query, offset, location=None):
        """Initial instance.

        :param id_: Unique identifier for this query.
        :param from_: Sender.
        :param query: Text of the query (up to 512 characters).
        :param offset: Offset of the results to be returned, can be controlled
            by the bot.
        :param location: Sender location, only for bots that request user
            location.

        """
        self.id = id_
        self.from_user = User(**from_)
        self.query = query
        self.offset = offset
        if location:
            self.location = Location(**location)

    def __str__(self):
        return '{}(id:{id}, from:{from_user}, query:{query})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


@_replace_args('id', 'from')
class CallbackQuery(_Query):
    """This class represents an incoming callback query from a callback button
    in an inline keyboard.

    """
    def __init__(self, id_, from_, message=None, inline_message_id=None,
                 chat_instance=None, data=None, game_short_name=None):
        """Initial instance.

        :param id_: Unique identifier for this query.
        :param from_: Sender.
        :param message: Message with the callback button that originated the
            query. Note that message content and message date will not be
            available if the message is too old.
        :param inline_message_id: Identifier of the message sent via the bot
            in inline mode, that originated the query.
        :param chat_instance: Global identifier, uniquely corresponding to the
            chat to which the message with the callback button was sent. Useful
            for high scores in games.
        :param data: Data associated with the callback button. Be aware that a
            bad client can send arbitrary data in this field.
        :param game_short_name: Short name of a Game to be returned, serves as
            the unique identifier for the game.

        """
        self.id = id_
        self.from_user = User(**from_)
        if message:
            self.message = Message(**message)
        self.inline_message_id = inline_message_id
        self.chat_instance = chat_instance
        self.data = data
        self.game_short_name = game_short_name

    def __str__(self):
        return '{}(id:{id}, from:{from_user}, data:{data})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


@_replace_args('from')
class ChosenInlineResult(_Query):
    """Represents a result of an inline query that was chosen by the user and
    sent to their chat partner.

    """
    def __init__(self, result_id, from_, query, location=None,
                 inline_message_id=None):
        """Initial instance.

        :param result_id: The unique identifier for the result that was chosen.
        :param from_: The user that chose the result.
        :param query: The query that was used to obtain the result.
        :param location: Sender location, only for bots that require user
            location,
        :param inline_message_id: Identifier of the sent inline message.
            Available only if there is an inline keyboard attached to the
            message. Will be also received in callback queries and can be used
            to edit the message.

        """
        self.id = result_id
        self.from_user = User(**from_)
        self.query = query
        self.location = Location(**location)
        self.inline_message = inline_message_id

    def __str__(self):
        return '{}(id:{id}, from:{from_user}, query:{query})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


class ResponseParameters(_Content):
    """Contains information about why a request was unsuccessful."""

    def __init__(self, migrate_to_chat_id=None, retry_after=None):
        """Initial instance.

        :param migrate_to_chat_id: The group has been migrated to a supergroup
            with the specified identifier. This number may be greater than 32
            bits and some programming languages may have difficulty/silent
            defects in interpreting it. But it is smaller than 52 bits, so a
            signed 64 bit integer or double-precision float type are safe for
            storing this identifier.
        :param retry_after: In case of exceeding flood control, the number of
            seconds left to wait before the request can be repeated.

        """
        self.migrate_to_chat_id = migrate_to_chat_id
        self.retry_after = retry_after


class BadRequest(object):
    """This class represents failed request."""

    def __init__(self, error_code, description, parameters=None):
        """Initial instance.

        :param error_code: Error code.
        :param description: Error description.
        :param parameters: ResponseParameters.

        """
        self.error_code = error_code
        self.description = description.replace('Bad Request: ', '')
        if parameters:
            self.parameters = ResponseParameters(**parameters)

    def __str__(self):
        return '{}(error_code:{error_code}, ' \
               'description:{description})'.format(self.__class__.__name__,
                                                   **self.__dict__)


class Game(_Content):
    """This class represents a game."""

    def __init__(self, title, description, photo, text=None, animation=None,
                 text_entities=None):
        """Initial instance.

        :param title: Title of the game.
        :param description: Description of the game.
        :param photo: Photo that will be displayed in the game message in
            chats.
        :param text: Brief description of the game or high scores included in
            the game message. Can be automatically edited to include current
            high scores for the game when the bot calls set_game_score, or
            manually edited using edit_message_text. 0-4096 characters.
        :param animation: Animation that will be displayed in the game message
            in chats.
        :param text_entities:  Special entities that appear in text, such as
            usernames, URLs, bot commands, etc.

        """
        self.title = title
        self.description = description
        self.photo = PhotoSize.from_list(photo)
        self.text = text
        if animation:
            self.animation = Animation(**animation)
        if text_entities:
            self.text_entities = MessageEntity.from_list(text_entities)

    def __str__(self):
        return '{}(title{title}, description:{description})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


class Animation(_Content):
    """This object represents an animation file to be displayed in the message
    containing a game.

    """
    def __init__(self, file_id, thumb=None, file_name=None, mime_type=None,
                 file_size=None):
        """Initial instance.

        :param file_id: Unique file identifier.
        :param thumb: Animation thumbnail as defined by sender.
        :param file_name: Original animation filename as defined by sender.
        :param mime_type: MIME type of the file as defined by sender.
        :param file_size: File size.

        """
        self.file_id = file_id
        if thumb:
            self.thumb = PhotoSize(**thumb)
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size


class GameHighScore(_Content):
    """This object represents one row of the high scores table for a game."""

    def __init__(self, position, user, score):
        """Initial instance.

        :param position: Position in high score table for the game.
        :param user: User.
        :param score: Score.

        """
        self.position = position,
        self.user = User(**user)
        self.score = score

    def __str__(self):
        return '{}(position{position}, user:{user}, score:{score})'.format(
            self.__class__.__name__,
            **self.__dict__
        )


class ShippingAddress(object):
    """This class represents a shipping address."""

    def __init__(self, country_code, state, city, street_line1, street_line2,
                 post_code):
        """Initial instance.

        :param country_code: ISO 3166-1 alpha-2 country code.
        :param state: State, if applicable.
        :param city: City.
        :param street_line1: First line for the address.
        :param street_line2: Second line for the address.
        :param post_code: Address post code.

        """
        self.country_code = country_code
        self.state = state
        self.city = city
        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.post_code = post_code


class OrderInfo(object):
    """This class represents information about an order."""

    def __init__(self, name=None, phone_number=None, email=None,
                 shipping_address=None):
        """Initial instance.

        :param name: User name.
        :param phone_number: User's phone number.
        :param email: User email.
        :param shipping_address: ShippingAddress.

        """
        self.name = name
        self.phone_number = phone_number
        self.email = email
        if shipping_address:
            self.shipping_address = ShippingAddress(**shipping_address)


class Invoice(object):
    """This class contains basic information about an invoice."""

    def __init__(self, title, description, start_parameter, currency,
                 total_amount):
        """Initial instance.

        :param title: Product name.
        :param description: Product description.
        :param start_parameter: Unique bot deep-linking parameter that can be
            used to generate this invoice.
        :param currency: Three-letter ISO 4217 currency code.
        :param total_amount: Total price in the smallest units of the currency
            (integer, not float/double). For example, for a price of US$ 1.45
            pass amount = 145. See:
            https://core.telegram.org/bots/payments#supported-currencies

        """
        self.title = title
        self.description = description
        self.start_parameter = start_parameter
        self.currency = currency
        self.total_amount = total_amount


class LabeledPrice(DictItem):
    """This class represents a portion of the price for goods or services."""

    def __init__(self, label, amount):
        """Initial instance.

        :param label: Portion label.
        :param amount: Price of the product in the smallest units of the
            currency (integer, not float/double). For example, for a price of
            US$ 1.45 pass amount = 145. See:
            https://core.telegram.org/bots/payments#supported-currencies

        """
        self.label = label
        self.amount = amount


class ShippingOption(DictItem):
    """This class represents one shipping option."""

    def __init__(self, id_, title, prices):
        """Initial instance.

        :param id_: Shipping option identifier.
        :param title: Option title.
        :param prices: List of LabeledPrice.

        """
        self.id = id_
        self.title = title
        self.prices = prices

    def to_dict(self):
        """Represents an object as a dictionary."""

        self.prices = [price.to_dict() for price in self.prices]
        return super(ShippingOption, self).to_dict()


@_replace_args('id', 'from')
class ShippingQuery(_Query):
    """This class contains information about an incoming shipping query."""

    def __init__(self, id_, from_, invoice_payload, shipping_address):
        """Initial instance.

        :param id_: Unique query identifier.
        :param from_: User who sent the query.
        :param invoice_payload: Bot specified invoice payload.
        :param shipping_address: ShippingAddress.

        """
        self.id = id_
        self.from_user = User(**from_)
        self.invoice_payload = invoice_payload
        self.shipping_address = ShippingAddress(**shipping_address)


@_replace_args('id', 'from')
class PreCheckoutQuery(_Query):
    """This class contains information about an incoming pre-checkout query."""

    def __init__(self, id_, from_, currency, total_amount, invoice_payload,
                 shipping_option_id=None, order_info=None):
        """Initial instance.

        :param id_: Unique query identifier.
        :param from_: User who sent the query.
        :param currency: Three-letter ISO 4217 currency code.
        :param total_amount: Total price in the smallest units of the currency
            (integer, not float/double). For example, for a price of US$ 1.45
            pass amount = 145. See:
            https://core.telegram.org/bots/payments#supported-currencies
        :param invoice_payload: Bot specified invoice payload.
        :param shipping_option_id: Identifier of the shipping option chosen by
            the user.
        :param order_info: OrderInfo.

        """
        self.id = id_
        self.from_user = User(**from_)
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        if order_info:
            self.order_info = OrderInfo(**order_info)


class SuccessfulPayment(object):
    """This class contains basic information about a successful payment."""

    def __init__(self, currency, total_amount, invoice_payload,
                 telegram_payment_charge_id, provider_payment_charge_id,
                 shipping_option_id=None, order_info=None):
        """Initial instance.

        :param currency: Three-letter ISO 4217 currency code.
        :param total_amount: Total price in the smallest units of the currency
            (integer, not float/double). For example, for a price of US$ 1.45
            pass amount = 145. See:
             https://core.telegram.org/bots/payments#supported-currencies
        :param invoice_payload: Bot specified invoice payload.
        :param telegram_payment_charge_id: Identifier of the shipping option
            chosen by the user.
        :param provider_payment_charge_id: Provider payment identifier.
        :param shipping_option_id: Identifier of the shipping option chosen by
            the user.
        :param order_info: OrderInfo.

        """
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        self.telegram_payment_charge_id = telegram_payment_charge_id
        self.provider_payment_charge_id = provider_payment_charge_id
        if order_info:
            self.order_info = OrderInfo(**order_info)
