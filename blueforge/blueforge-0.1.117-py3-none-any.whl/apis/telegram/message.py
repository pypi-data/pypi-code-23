class Message(object):
    def __init__(self, reply_to_message_id=None, disable_notification=None, reply_markup=None):
        self.reply_to_message_id = reply_to_message_id
        self.disable_notification = disable_notification
        self.reply_markup = reply_markup

    def get_method(self):
        return self.method

    def get_data(self):
        data = {}

        if self.reply_markup:
            data['reply_markup'] = self.reply_markup.get_data()

        if self.reply_to_message_id:
            data['reply_to_message_id'] = self.reply_to_message_id

        if self.disable_notification:
            data['disable_notification'] = self.disable_notification

        # SendMessage
        if hasattr(self, 'text') and self.text:
            data['text'] = self.text

        if hasattr(self, 'parse_mode') and self.parse_mode:
            data['parse_mode'] = self.parse_mode

        if hasattr(self, 'disable_web_page_preview') and self.disable_web_page_preview:
            data['disable_web_page_preview'] = self.disable_web_page_preview

        # SendPhoto
        if hasattr(self, 'photo') and self.photo:
            data['photo'] = self.photo

        if hasattr(self, 'caption') and self.caption:
            data['caption'] = self.caption

        # SendAudio
        if hasattr(self, 'audio') and self.audio:
            data['audio'] = self.audio

        if hasattr(self, 'duration') and self.duration:
            data['duration'] = self.duration

        if hasattr(self, 'performer') and self.performer:
            data['performer'] = self.performer

        if hasattr(self, 'title') and self.title:
            data['title'] = self.title

        # SendDocument
        if hasattr(self, 'document') and self.document:
            data['document'] = self.document

        # SendVideo
        if hasattr(self, 'video') and self.video:
            data['video'] = self.video

        if hasattr(self, 'width') and self.width:
            data['width'] = self.width

        if hasattr(self, 'height') and self.height:
            data['height'] = self.height

        # SendVoice, SendVideoNote, SendMediaGroup is passed due to deadline
        # SendLocation
        if hasattr(self, 'latitude') and self.latitude:
            data['latitude'] = self.latitude

        if hasattr(self, 'longitude') and self.longitude:
            data['longitude'] = self.longitude

        if hasattr(self, 'live_period') and self.live_period:
            data['live_period'] = self.live_period

        return data


class SendMessage(Message):
    method = 'sendMessage'

    def __init__(self, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None,
                 reply_to_message_id=None, reply_markup=None):
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        super(SendMessage, self).__init__(reply_to_message_id=reply_to_message_id,
                                          disable_notification=disable_notification, reply_markup=reply_markup)


class SendPhoto(Message):
    method = 'sendPhoto'

    def __init__(self, photo, caption=None, disable_notification=None, reply_to_message_id=None,
                 reply_markup=None, parse_mode=None):
        self.photo = photo
        self.caption = caption
        self.parse_mode = parse_mode
        super(SendPhoto, self).__init__(reply_to_message_id=reply_to_message_id,
                                        disable_notification=disable_notification, reply_markup=reply_markup)


class SendAudio(Message):
    method = 'sendAudio'

    def __init__(self, audio, caption=None, duration=None, performer=None, title=None,
                 disable_notification=None, reply_to_message_id=None, reply_markup=None, parse_mode=None):
        self.audio = audio
        self.caption = caption
        self.duration = duration
        self.performer = performer
        self.title = title
        self.parse_mode = parse_mode
        super(SendAudio, self).__init__(reply_to_message_id=reply_to_message_id,
                                        disable_notification=disable_notification, reply_markup=reply_markup)


class SendDocument(Message):
    method = 'sendDocument'

    def __init__(self, document, caption=None, disable_notification=None, reply_to_message_id=None,
                 reply_markup=None, parse_mode=None):
        self.document = document
        self.caption = caption
        self.parse_mode = parse_mode
        super(SendDocument, self).__init__(reply_to_message_id=reply_to_message_id,
                                           disable_notification=disable_notification, reply_markup=reply_markup)


class SendVideo(Message):
    method = 'sendVideo'

    def __init__(self, video, caption=None, duration=None, width=None, height=None,
                 disable_notification=None, reply_to_message_id=None, reply_markup=None, parse_mode=None):
        self.video = video
        self.caption = caption
        self.duration = duration
        self.width = width
        self.height = height
        self.parse_mode = parse_mode
        super(SendVideo, self).__init__(reply_to_message_id=reply_to_message_id,
                                        disable_notification=disable_notification, reply_markup=reply_markup)


class SendLocation(Message):
    method = 'sendLocation'

    def __init__(self, latitude, longitude, live_period=None,
                 disable_notification=None, reply_to_message_id=None, reply_markup=None):
        self.latitude = latitude
        self.longitude = longitude
        self.live_period = live_period
        super(SendLocation, self).__init__(reply_to_message_id=reply_to_message_id,
                                           disable_notification=disable_notification, reply_markup=reply_markup)
