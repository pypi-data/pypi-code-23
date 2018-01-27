import json


class MessageClass(object):
    def __init__(self, message_text=""):
        self._message_text = message_text
        self._attachments = []
        self._data = {}
        self._error = {}
        self._logs = []

    @property
    def message_text(self):
        return self._message_text

    @message_text.setter
    def message_text(self, message_text):
        self._message_text = message_text

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        try:
            data_json = json.dumps(data)
        except TypeError:
            raise TypeError("'data' must be JSON serializable")
        self._data = data

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    @property
    def logs(self):
        return self._logs

    def __repr__(self):
        to_dict = {"message_text": self._message_text}
        return json.dumps(to_dict)

    def attach(self, attachment):
        """ Checks if attachment is of valid class (MessageAttachmentsClass) and adds
		corresponding attachment if not raises TypeError """
        if not isinstance(attachment, MessageAttachmentsClass):
            raise TypeError("Attachment must be MessageAttachmentsClass() object")
        else:
            self._attachments.append(attachment.get_dict())

    def add_log(self, log):
        """ Checks if attachment is of valid class (MessageAttachmentsClass) and adds
		corresponding attachment if not raises TypeError """
        if not isinstance(log, LogClass):
            raise TypeError("Log must be LogClass() object")
        else:
            self._logs.append(log.get_dict())

    def to_json(self, **kwargs):
        """ Returns object in json format with optional kwargs. **kwargs are passed as is to
		json object kwargs. If kwargs are not provided it defaults to "sort_keys=True, indent=4, separators=(",", ": ")"
		For unsorted pass, sort_keys=False """
        message = {"attachments": self._attachments,
                   "message_text": self._message_text, "data": self._data, "error": self._error, "logs": self._logs
                   }
        if kwargs == {}:
            return json.dumps(message, sort_keys=True, indent=4, separators=(",", ": "))
        else:
            return json.dumps(message, **kwargs)

    def get_dict(self, **kwargs):
        """ Returns object in dict format.
        """
        message = {"attachments": self._attachments,
                   "message_text": self._message_text, "data": self._data, "error": self._error, "logs": self._logs
                   }

        return message


class MessageAttachmentsClass(object):
    """Class Description"""

    def __init__(self, image_url="", thumb_url="", color="", text="",
                 author_name="", author_icon="", author_link="", footer="", footer_icon="",
                 pretext="", title="", title_link="", status=0, ts=0):

        self._image_url = image_url
        self._thumb_url = thumb_url
        self._color = color
        self._text = text
        self._author_name = author_name
        self._author_icon = author_icon
        self._author_link = author_link
        self._footer = footer
        self._footer_icon = footer_icon
        self._pretext = pretext
        self._title = title
        self._title_link = title_link
        self._ts = ts
        self._fields = []
        self._buttons = []
        if isinstance(status, int):
            self._status = status
        else:
            raise TypeError("Status must be an integer")

    @property
    def image_url(self):
        return self._image_url

    @property
    def thumb_url(self):
        return self._thumb_url

    @property
    def color(self):
        return self._color

    @property
    def text(self):
        return self._text

    @property
    def author_icon(self):
        return self._author_icon

    @property
    def author_name(self):
        return self._author_name

    @property
    def author_link(self):
        return self._author_link

    @property
    def footer(self):
        return self._footer

    @property
    def footer_icon(self):
        return self._footer_icon

    @property
    def pretext(self):
        return self._pretext

    @property
    def title(self):
        return self._title

    @property
    def title_link(self):
        return self._title_link

    @property
    def status(self):
        return self._status

    @property
    def ts(self):
        return self._ts

    @image_url.setter
    def image_url(self, image_url):
        self._image_url = image_url

    @thumb_url.setter
    def thumb_url(self, thumb_url):
        self._thumb_url = thumb_url

    @color.setter
    def color(self, color):
        self._color = color

    @text.setter
    def text(self, text):
        self._text = text

    @author_name.setter
    def author_name(self, author_name):
        self._author_name = author_name

    @author_icon.setter
    def author_icon(self, author_icon):
        self._author_icon = author_icon

    @author_link.setter
    def author_link(self, author_link):
        self._author_link = author_link

    @footer.setter
    def footer(self, footer):
        self._footer = footer

    @footer_icon.setter
    def footer_icon(self, footer_icon):
        self._footer_icon = footer_icon

    @pretext.setter
    def pretext(self, pretext):
        self._pretext = pretext

    @title.setter
    def title(self, title):
        self._title = title

    @title_link.setter
    def title_link(self, title_link):
        self._title_link = title_link

    @status.setter
    def status(self, status):
        if isinstance(status, int):
            self._status = status
        else:
            raise TypeError("Status must be an integer")

    @ts.setter
    def ts(self, ts):
        if isinstance(ts, int):
            self._ts = ts
        else:
            raise TypeError("Timestamp must be an Unix timestamp integer")

    def __repr__(self):
        _to_dict = {"image_url": self._image_url, "thumb_url": self._thumb_url, "color": self._color,
                    "text": self._text, "author_name": self._author_name, "author_icon": self.author_icon,
                    "footer": self._footer, "footer_icon": self._footer_icon, "pretext": self._pretext,
                    "title": self._title, "title_link": self._title_link, "status": self._status,
                    "fields": self._fields, "buttons": self._buttons}
        return json.dumps(_to_dict)

    def attach_field(self, attachment_field):
        """Checks if passed arg is of class AttachmentFieldsClass, if not raises TypeError else adds Field
		"""
        if not isinstance(attachment_field, AttachmentFieldsClass):
            raise TypeError("Field should be an AttachmentFieldsClass object")
        else:
            self._fields.append(attachment_field.get_dict())

    def attach_button(self, button_field):
        """Checks if passed arg is of class MessageButtonsClass, if not raises TypeError else adds button """
        if not isinstance(button_field, MessageButtonsClass):
            raise TypeError("Button should be an MessageButtonsClass object")
        else:
            self._buttons.append(button_field.get_dict())

    def get_dict(self):
        """Returns MessageAttachmentsClass object as dictionary object"""
        return {"image_url": self._image_url, "thumb_url": self._thumb_url, "color": self._color,
                "text": self._text, "author_name": self._author_name, "author_icon": self.author_icon,
                "author_link": self._author_link, "ts": self._ts,
                "footer": self._footer, "footer_icon": self._footer_icon, "pretext": self._pretext,
                "title": self._title, "title_link": self._title_link, "status": self._status,
                "fields": self._fields, "buttons": self._buttons}


class AttachmentFieldsClass(object):
    def __init__(self, title="", short=1, value=""):
        self._title = title
        if isinstance(short, int):
            self._short = short
        else:
            raise TypeError("Short must be an integer")
        self.value = value

    @property
    def title(self):
        return self._title

    @property
    def short(self):
        return self._short

    @property
    def value(self):
        return self._value

    @title.setter
    def title(self, title):
        self._title = title

    @short.setter
    def short(self, short):
        if isinstance(short, int):
            self._short = short
        else:
            raise TypeError("Short must be an integer")

    @value.setter
    def value(self, value):
        self._value = value

    def __repr__(self):
        to_dict = {"title": self._title, "short": self._short, "value": self._value}
        return json.dumps(to_dict)

    def get_dict(self):
        """Returns AttachmentFieldsClass object as dictionary object"""
        return {"title": self._title, "short": self._short, "value": self._value}


class MessageButtonsClass(object):
    def __init__(self, value="value", name="name", text="", command={}):
        self._value = value
        self._name = name
        self._text = text
        self._command = command

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name

    @property
    def text(self):
        return self._text

    @property
    def command(self):
        return self._command

    @value.setter
    def value(self, value):
        self._value = value

    @name.setter
    def name(self, name):
        self._name = name

    @text.setter
    def text(self, text):
        self._text = text

    @command.setter
    def command(self, command):
        self._command = command

    def __repr__(self):
        to_dict = {"value": self._value, "name": self._name,
                   "text": self._text, "command": self._command}
        return json.dumps(to_dict)

    def get_dict(self):
        """Returns MessageButtonsClass object as dictionary object"""
        return {"value": self._value, "name": self._name,
                "text": self._text, "command": self._command}


class ErrorClass(object):
    def __init__(self, code="", name="", text=""):
        self._code = code
        self._name = name
        self._text = text

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    @property
    def text(self):
        return self._text

    @code.setter
    def code(self, code):
        self._code = code

    @name.setter
    def name(self, name):
        self._name = name

    @text.setter
    def text(self, text):
        self._text = text


class LogClass(object):
    def __init__(self, tag="", name="", text=""):
        self._tag = tag
        self._name = name
        self._text = text

    @property
    def tag(self):
        return self._tag

    @property
    def name(self):
        return self._name

    @property
    def text(self):
        return self._text

    @tag.setter
    def tag(self, tag):
        self._tag = tag

    @name.setter
    def name(self, name):
        self._name = name

    @text.setter
    def text(self, text):
        self._text = text
