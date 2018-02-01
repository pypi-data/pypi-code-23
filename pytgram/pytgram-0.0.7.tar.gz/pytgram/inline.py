"""inline module.

This module describes the Inline content to answer inlineQuery.

"""


from uuid import uuid4

from .content import DictItem


class _InlineQueryResult(DictItem):
    """Base class."""

    _result_type = None
    _prefix = None

    def __init__(self, result_id=None, url=None, title=None, width=None,
                 height=None, thumb_url=None, thumb_width=None, caption=None,
                 thumb_height=None, file_id=None, description=None,
                 duration=None, mime_type=None, reply_markup=None,
                 input_message_content=None):
        """Initial instance.

        :param result_id: Unique identifier for this result, 1-64 bytes.
        :param url: URL of the result.
        :param title: Title of the result.
        :param width: Width of the result (photo, video, etc.).
        :param height: Height of the result (photo, video, etc.).
        :param thumb_url: URL of the thumbnail for the result.
        :param thumb_width: Thumbnail width.
        :param thumb_height: Thumbnail height.
        :param caption: Caption of the result to be sent, 0-200 characters.
        :param file_id: A valid file identifier of result cached.
        :param description: Short description of the result.
        :param duration: Duration in seconds.
        :param mime_type: Mime type of the content.
        :param reply_markup: Inline keyboard attached to the message.
        :param input_message_content: Content of the message to be sent.

        """
        self.id = result_id or uuid4().hex
        self.title = title
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
        self.description = description
        self.caption = caption
        self.mime_type = mime_type
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content

        self._prefix = self._prefix or self._result_type

        for attr, value in zip(
                ('url', 'width', 'height', 'duration', 'file_id'),
                (url, width, height, duration, file_id)
        ):
            setattr(self, '%s_%s' % (self._prefix, attr), value)

    def __str__(self):
        return '{}(id:{})'.format(self.__class__.__name__, self.id)

    @property
    def result_type(self):
        return self._result_type

    def to_dict(self):
        """Represents an object as a dictionary."""

        if self.input_message_content:
            self.input_message_content = self.input_message_content.to_dict()
        obj_dict = super(_InlineQueryResult, self).to_dict()
        obj_dict['type'] = self._result_type
        return obj_dict


class _InlineQueryResultImage(_InlineQueryResult):
    """Base constructor for image classes."""

    def __init__(self, url, thumb_url, **kwargs):
        super(_InlineQueryResultImage, self).__init__(
            url=url, thumb_url=thumb_url, **kwargs
        )


class _InlineQueryResultAudio(_InlineQueryResult):
    """Base constructor for audio classes."""

    def __init__(self, url, title, **kwargs):
        super(_InlineQueryResultAudio, self).__init__(
            url=url, title=title, **kwargs
        )


class _InlineQueryResultCached(_InlineQueryResult):
    """Base constructor for cached classes."""

    def __init__(self, file_id, **kwargs):
        super(_InlineQueryResultCached, self).__init__(
            file_id=file_id, **kwargs
        )


class _InlineQueryResultCachedTitle(_InlineQueryResult):
    """Base constructor for cached classes."""

    def __init__(self, file_id, title, **kwargs):
        super(_InlineQueryResultCachedTitle, self).__init__(
            file_id=file_id, title=title, **kwargs
        )


class InlineQueryResultPhoto(_InlineQueryResultImage):
    """Represents a link to a photo. By default, this photo will be sent by the
    user with optional caption. Alternatively, you can use
    input_message_content to send a message with the specified content instead
    of the photo.

    """
    _result_type = 'photo'


class InlineQueryResultGif(_InlineQueryResultImage):
    """Represents a link to an animated GIF file. By default, this animated GIF
    file will be sent by the user with optional caption. Alternatively, you can
    use input_message_content to send a message with the specified content
    instead of the animation.

    :param gif_duration: Duration of the GIF.
    :param kwargs: Keyword arguments for _InlineQueryResultImage.

    """
    _result_type = 'gif'

    def __init__(self, gif_duration=None, **kwargs):
        super(InlineQueryResultGif, self).__init__(**kwargs)
        self.gif_duration = gif_duration


class InlineQueryResultMpeg4Gif(_InlineQueryResultImage):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video without
    sound). By default, this animated MPEG-4 file will be sent by the user with
    optional caption. Alternatively, you can use input_message_content to send
    a message with the specified content instead of the animation.

    :param mpeg4_duration: Video duration.
    :param kwargs: Keyword arguments for _InlineQueryResultImage.

    """
    _result_type = 'mpeg4_gif'
    _prefix = 'mpeg4'

    def __init__(self, mpeg4_duration=None, **kwargs):
        super(InlineQueryResultMpeg4Gif, self).__init__(**kwargs)
        self.mpeg4_duration = mpeg4_duration


class InlineQueryResultAudio(_InlineQueryResultAudio):
    """Represents a link to an mp3 audio file. By default, this audio file will
    be sent by the user. Alternatively, you can use input_message_content to
    send a message with the specified content instead of the audio.

    """
    _result_type = 'audio'


class InlineQueryResultVoice(_InlineQueryResultAudio):
    """Represents a link to a voice recording in an .ogg container encoded with
    OPUS. By default, this voice recording will be sent by the user.
    Alternatively, you can use input_message_content to send a message with the
    specified content instead of the the voice message.

    """
    _result_type = 'voice'


class InlineQueryResultArticle(_InlineQueryResult):
    """Represents a link to an article or web page."""

    _result_type = 'article'

    def __init__(self, title, input_message_content, hide_url=None, **kwargs):
        """Initial instance.

        :param title: Title of the result.
        :param input_message_content: Content of the message to be sent (
            InputTextMessageContent, InputLocationMessageContent,
            InputVenueMessageContent, InputContactMessageContent).
        :param kwargs: url, description, thumb_url, thumb_width, thumb_height,
            reply_markup.

        """
        super(InlineQueryResultArticle, self).__init__(
            title=title, input_message_content=input_message_content, **kwargs
        )
        self.hide_url = hide_url


class InlineQueryResultVideo(_InlineQueryResult):
    """Represents a link to a page containing an embedded video player or a
    video file. By default, this video file will be sent by the user with an
    optional caption. Alternatively, you can use input_message_content to send
    a message with the specified content instead of the video.

    """
    _result_type = 'video'

    def __init__(self, url, thumb_url, title, mime_type, **kwargs):
        """Initial instance.

        :param url: A valid URL for the embedded video player or video file.
        :param thumb_url: URL of the thumbnail (jpeg only) for the video.
        :param title: Title for the result.
        :param mime_type: Mime type of the content of video url, 'text/html' or
            'video/mp4'.
        :param kwargs: caption, width. height, duration, description,
            reply_markup, input_message_content.

        """
        super(InlineQueryResultVideo, self).__init__(
            url=url,
            thumb_url=thumb_url,
            title=title,
            mime_type=mime_type,
            **kwargs
        )


class InlineQueryResultDocument(_InlineQueryResult):
    """Represents a link to a file. By default, this file will be sent by the
    user with an optional caption. Alternatively, you can use
    input_message_content to send a message with the specified content instead
    of the file. Currently, only .PDF and .ZIP files can be sent using this
    method.

    """
    _result_type = 'document'

    def __init__(self, url, title, mime_type, **kwargs):
        """Initial instance.

        :param url: A valid URL for the file.
        :param title: Title for the result.
        :param mime_type: Mime type of the content of the file, either
            'application/pdf' or 'application/zip'.
        :param kwargs: thumb_url, thumb_width, thumb_height, description,
            caption, reply_markup, input_message_content.

        """
        super(InlineQueryResultDocument, self).__init__(
            url=url, title=title, mime_type=mime_type, **kwargs
        )


class InlineQueryResultLocation(_InlineQueryResult):
    """Represents a location on a map. By default, the location will be sent by
    the user. Alternatively, you can use input_message_content to send a
    message with the specified content instead of the location.

    """
    _result_type = 'location'

    def __init__(self, latitude, longitude, title, **kwargs):
        """Initial instance.

        :param latitude: Location latitude in degrees.
        :param longitude: Location longitude in degrees.
        :param title: Location title.
        :param kwargs: thumb_url, thumb_width, thumb_height, reply_markup,
            input_message_content.

        """
        super(InlineQueryResultLocation, self).__init__(title=title, **kwargs)
        self.latitude = latitude
        self.longitude = longitude


class InlineQueryResultVenue(InlineQueryResultLocation):
    """Represents a venue. By default, the venue will be sent by the user.
    Alternatively, you can use input_message_content to send a message with the
    specified content instead of the venue.

    """
    _result_type = 'venue'

    def __init__(self, latitude, longitude, title, address, **kwargs):
        """Initial instance.

        :param latitude: Latitude of the venue location in degrees.
        :param longitude: Longitude of the venue location in degrees.
        :param title: Title of the venue.
        :param address: Address of the venue.
        :param kwargs: thumb_url, thumb_width, thumb_height, foursquare_id,
            reply_markup, input_message_content.

        """
        super(InlineQueryResultVenue, self).__init__(
            latitude=latitude, longitude=longitude, title=title, **kwargs
        )
        self.address = address


class InlineQueryResultContact(_InlineQueryResult):
    """Represents a contact with a phone number. By default, this contact will
    be sent by the user. Alternatively, you can use input_message_content to
    send a message with the specified content instead of the contact.

    """
    _result_type = 'contact'

    def __init__(self, phone_number, first_name, last_name=None, **kwargs):
        """Initial instance.

        :param phone_number: Contact's phone number.
        :param first_name: Contact's first name.
        :param last_name: Contact's last name.
        :param kwargs: thumb_url, thumb_width, thumb_height, reply_markup,
            input_message_content.

        """
        super(InlineQueryResultContact, self).__init__(**kwargs)
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name


class InlineQueryResultGame(_InlineQueryResult):
    """Represents a Game."""

    _result_type = 'game'

    def __init__(self, game_short_name, **kwargs):
        """Initial instance.

        :param game_short_name: Short name of the game.
        :param kwargs: reply_markup.

        """
        super(InlineQueryResultGame, self).__init__(**kwargs)
        self.game_short_name = game_short_name


class InlineQueryResultCachedPhoto(_InlineQueryResultCached):
    """Represents a link to a photo stored on the Telegram servers. By default,
    this photo will be sent by the user with an optional caption.
    Alternatively, you can use input_message_content to send a message with the
    specified content instead of the photo.

    """
    _result_type = InlineQueryResultPhoto.result_type


class InlineQueryResultCachedGif(_InlineQueryResultCached):
    """Represents a link to an animated GIF file stored on the Telegram
    servers. By default, this animated GIF file will be sent by the user with
    an optional caption. Alternatively, you can use input_message_content to
    send a message with specified content instead of the animation.

    """
    _result_type = InlineQueryResultGif.result_type


class InlineQueryResultCachedMpeg4Gif(_InlineQueryResultCached):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video without
    sound) stored on the Telegram servers. By default, this animated MPEG-4
    file will be sent by the user with an optional caption. Alternatively, you
    can use input_message_content to send a message with the specified content
    instead of the animation.

    """
    _result_type = InlineQueryResultMpeg4Gif.result_type


class InlineQueryResultCachedSticker(_InlineQueryResultCached):
    """Represents a link to a sticker stored on the Telegram servers. By
    default, this sticker will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead
    of the sticker.

    """
    _result_type = 'sticker'


class InlineQueryResultCachedAudio(_InlineQueryResultCached):
    """Represents a link to an mp3 audio file stored on the Telegram servers.
    By default, this audio file will be sent by the user. Alternatively, you
    can use input_message_content to send a message with the specified content
    instead of the audio.

    """
    _result_type = InlineQueryResultAudio.result_type


class InlineQueryResultCachedDocument(_InlineQueryResultCachedTitle):
    """Represents a link to a file stored on the Telegram servers. By default,
    this file will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with the specified
    content instead of the file.

    """
    _result_type = InlineQueryResultDocument.result_type


class InlineQueryResultCachedVideo(_InlineQueryResultCachedTitle):
    """Represents a link to a video file stored on the Telegram servers. By
    default, this video file will be sent by the user with an optional caption.
    Alternatively, you can use input_message_content to send a message with the
    specified content instead of the video.

    """
    _result_type = InlineQueryResultVideo.result_type


class InlineQueryResultCachedVoice(_InlineQueryResultCachedTitle):
    """Represents a link to a voice message stored on the Telegram servers. By
    default, this voice message will be sent by the user. Alternatively, you
    can use input_message_content to send a message with the specified content
    instead of the voice message.

    """
    _result_type = InlineQueryResultVoice.result_type


class InputTextMessageContent(DictItem):
    """Represents the content of a text message to be sent as the result of an
    inline query.

    """
    def __init__(self, message_text, parse_mode=None,
                 disable_web_page_preview=None):
        """Initial instance.

        :param message_text: Text of the message to be sent, 1-4096 characters.
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to
            show bold, italic, fixed-width text or inline URLs in your bot's
            message.
        :param disable_web_page_preview: Disables link previews for links in
            the sent message.

        """
        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview


class InputLocationMessageContent(DictItem):
    """Represents the content of a location message to be sent as the result of
    an inline query.

    """
    def __init__(self, latitude, longitude):
        """Initial instance.

        :param latitude: Latitude of the location in degrees.
        :param longitude: Longitude of the location in degrees.

        """
        self.latitude = latitude
        self.longitude = longitude


class InputVenueMessageContent(InputLocationMessageContent):
    """Represents the content of a venue message to be sent as the result of an
    inline query.

    """
    def __init__(self, latitude, longitude, title, address,
                 foursquare_id=None):
        """Initial instance.
        :param latitude: Latitude of the venue in degrees.
        :param longitude: Longitude of the venue in degrees.
        :param title: Name of the venue.
        :param address: Address of the venue.
        :param foursquare_id: Foursquare identifier of the venue, if known.

        """
        super(InputVenueMessageContent, self).__init__(latitude, longitude)
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id


class InputContactMessageContent(DictItem):
    """Represents the content of a contact message to be sent as the result of
    an inline query.

    """
    def __init__(self, phone_number, first_name, last_name=None):
        """Initial instance.

        :param phone_number: Contact's phone number.
        :param first_name: Contact's first name.
        :param last_name: Contact's last name.

        """
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
