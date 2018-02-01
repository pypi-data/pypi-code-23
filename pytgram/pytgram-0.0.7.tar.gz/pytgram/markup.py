"""markup module.

This module contains the entities allowing to create the layout of the keyboard
for more convenient use of the functions of the bot.

"""


from .content import DictItem


class _Keyboard(DictItem):
    """Base keyboard class."""

    def __init__(self, keyboard=None):
        """Initial instance.

        :param keyboard: List of rows, where row is list of buttons.

        """
        self.keyboard = keyboard if keyboard else []

    def __str__(self):
        return '{}(keyboard{})'.format(self.__class__.__name__, self.keyboard)

    def add_button_row(self, row):
        """Appends buttons row to keyboard."""

        self.keyboard.append(row)

    def to_dict(self):
        """Represents an object as a dictionary."""

        keyboard = []
        for button_row in self.keyboard:
            keyboard.append([button.to_dict() for button in button_row])
        self.keyboard = keyboard
        return super(_Keyboard, self).to_dict()


class _Button(DictItem):
    """Base button class."""

    def __init__(self, text):
        """Initial instance.

        :param text: Text of the button. If none of the optional fields are
            used, it will be sent to the bot as a message when the button is
            pressed.

        """
        self.text = text

    def __str__(self):
        return '{}(text:{})'.format(self.__class__.__name__, self.text)


class KeyboardButton(_Button):
    """This class represents one button of the reply keyboard."""

    def __init__(self, text, request_contact=None, request_location=None):
        """Initial instance.

        :param text: Text of the button. If none of the optional fields are
            used, it will be sent to the bot as a message when the button is
            pressed.
        :param request_contact: If True, the user's phone number will be sent
            as a contact when the button is pressed. Available in private
            chats only.
        :param request_location: If True, the user's current location will be
            sent when the button is pressed. Available in private chats only.

        """
        super(KeyboardButton, self).__init__(text)
        self.request_contact = request_contact
        self.request_location = request_location


class ReplyKeyboardMarkup(_Keyboard):
    """This class represents a custom keyboard with reply options."""

    def __init__(self, keyboard=None, resize_keyboard=None,
                 one_time_keyboard=None, selective=None):
        """Initial instance.

        :param keyboard: List of button rows, each represented by an List of
            KeyboardButton objects.
        :param resize_keyboard: Requests clients to resize the keyboard
            vertically for optimal fit (e.g., make the keyboard smaller if
            there are just two rows of buttons). Defaults to false, in which
            case the custom keyboard is always of the same height as the app's
            standard keyboard.
        :param one_time_keyboard: Requests clients to hide the keyboard as soon
            as it's been used. The keyboard will still be available, but
            clients will automatically display the usual letter-keyboard in the
            chat – the user can press a special button in the input field to
            see the custom keyboard again. Defaults to false.
        :param selective: Use this parameter if you want to show the keyboard
            to specific users only. Targets: 1) users that are @mentioned in
            the text of the Message object; 2) if the bot's message is a reply
            (has reply_to_message_id), sender of the original message.
            Example: A user requests to change the bot‘s language, bot replies
            to the request with a keyboard to select the new language. Other
            users in the group don’t see the keyboard.

        """
        rows = None
        if keyboard:
            rows = [self._crete_button_row(*row) for row in keyboard]
        super(ReplyKeyboardMarkup, self).__init__(rows)
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    @staticmethod
    def _crete_button_row(*args):
        """Creates buttons row.

        :param args: Text for each buttons or KeyboardButton instances.
        :return: List of KeyboardButton instances.

        """
        button_row = []
        for arg in args:
            if not isinstance(arg, KeyboardButton):
                button = KeyboardButton(str(arg))
            else:
                button = arg
            button_row.append(button)
        return button_row

    def add_button_row(self, *args):
        """Appends buttons row to keyboard.

        :param args: Text for each buttons or KeyboardButton instances.

        """
        row = self._crete_button_row(*args)
        return super(ReplyKeyboardMarkup, self).add_button_row(row)


class ReplyKeyboardRemove(DictItem):
    """Upon receiving a message with this object, Telegram clients will remove
    the current custom keyboard and display the default letter-keyboard. By
    default, custom keyboards are displayed until a new keyboard is sent by a
    bot. An exception is made for one-time keyboards that are hidden
    immediately after the user presses a button.

    """
    def __init__(self, remove_keyboard=True, selective=None):
        """Initial instance.

        :param selective: Use this parameter if you want to remove the keyboard
            for specific users only. Targets: 1) users that are @mentioned in
            the text of the Message object; 2) if the bot's message is a reply
            (has reply_to_message_id), sender of the original message.
            Example: A user votes in a poll, bot returns confirmation message
            in reply to the vote and removes the keyboard for that user, while
            still showing the keyboard with poll options to users who haven't
            voted yet.
        :param remove_keyboard: Requests clients to remove the custom keyboard
            (user will not be able to summon this keyboard; if you want to hide
            the keyboard from sight but keep it accessible, use
            one_time_keyboard in ReplyKeyboardMarkup).

        """
        self.remove_keyboard = remove_keyboard
        self.selective = selective


class InlineKeyboardButton(_Button):
    """This class represents one button of an inline keyboard. You must use
    exactly one of the optional fields.

    """
    def __init__(self, text, url=None, callback_data=None, pay=None,
                 switch_inline_query=None, callback_game=None,
                 switch_inline_query_current_chat=None):
        """Initial instance.

        :param text: Label text on the button.
        :param url: HTTP url to be opened when button is pressed.
        :param callback_data: Data to be sent in a callback query to the bot
            when button is pressed, 1-64 bytes.
        :param pay: Specify True, to send a Pay button.
        :param switch_inline_query: If set, pressing the button will prompt the
            user to select one of their chats, open that chat and insert the
            bot‘s username and the specified inline query in the input field.
            Can be empty, in which case just the bot’s username will be
            inserted.
        :param callback_game: Description of the game that will be launched
            when the user presses the button.
            NOTE: This type of button must always be the first button in the
            first row.
        :param switch_inline_query_current_chat: If set, pressing the button
            will insert the bot‘s username and the specified inline query in
            the current chat's input field. Can be empty, in which case only
            the bot’s username will be inserted.

        """
        super(InlineKeyboardButton, self).__init__(text)
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = \
            switch_inline_query_current_chat
        self.callback_game = callback_game
        self.pay = pay


class InlineKeyboardMarkup(_Keyboard):
    """This object represents an inline keyboard that appears right next to the
    message it belongs to.

    """
    def to_dict(self):
        """Represents an object as a dictionary."""

        keyboard_dict = super(InlineKeyboardMarkup, self).to_dict()
        keyboard_dict['inline_keyboard'] = keyboard_dict.pop('keyboard')
        return keyboard_dict

    def add_button_row(self, *args):
        """Appends buttons row to keyboard.

        :param args: Must be InlineKeyboardButton instances.

        """
        super(InlineKeyboardMarkup, self).add_button_row(args)


class ForceReply(DictItem):
    """Upon receiving a message with this object, Telegram clients will display
    a reply interface to the user (act as if the user has selected the bot‘s
    message and tapped ’Reply'). This can be extremely useful if you want to
    create user-friendly step-by-step interfaces without having to sacrifice
    privacy mode.

    """

    def __init__(self, force_reply=True, selective=None):
        """Initial instance.

        :param force_reply: Shows reply interface to the user, as if they
            manually selected the bot‘s message and tapped 'Reply'.
        :param selective: Use this parameter if you want to force reply from
            specific users only. Targets: 1) users that are @mentioned in the
            text of the Message object; 2) if the bot's message is a reply
            (has reply_to_message_id), sender of the original message.

        """
        self.force_reply = force_reply
        self.selective = selective
