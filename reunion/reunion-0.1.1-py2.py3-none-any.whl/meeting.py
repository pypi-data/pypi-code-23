"""A library that captures a meeting notes, similar to Meetbot."""
from collections import namedtuple


class Meeting:
    """Capture and parses meetings."""

    def __init__(self):
        """Initial."""
        self.results = {
            'discussion': [],
            'topics': {},
            'actions': {},
            'users': {},
        }

        self.keywords = [
            '#startmeeting',
            '#topic',
            '#action',
            '#info',
            '#endmeeting',
        ]

        self._started = False
        self._start_topic = None
        self._start_info = None
        self._start_action = None

    def parse(self, message):
        """Parse meeting lines.

        Args:
            message (str): Conversation text.

        """
        msg = self.message_parser(message)
        self.keyword_parser(msg)

        if self._started:
            self.results['discussion'].append(msg.full_message)

            if msg.username not in self.results['users']:
                self.results['users'][msg.username] = {
                    'actions': [],
                    'message_count': 0,
                    'messages': [],
                }

            self.results['users'][msg.username]['message_count'] += 1
            self.results['users'][msg.username]['messages'].append(msg.text)

            if self._start_topic and not msg.action:
                self.results['topics'][self._start_topic]['discussion'].append(msg.full_message)

            if self._start_info and self._start_topic:
                self.results['topics'][self._start_topic]['info'].append(msg.text)

            if self._start_action:
                self.results['actions'][msg.username].append(msg.text)
                self.results['users'][msg.username]['actions'].append(msg.text)

        self._start_action = False
        self._start_info = False

    def message_parser(self, message):
        """Parse meeting lines into consumable attributes.

        Args:
            message (str): Conversation text.

        Returns:
            Message: A message object with attributes.

        """
        attributes = [
            'username',
            'full_message',
            'action',
            'text',
            'channel',
        ]

        message_obj = namedtuple('Message', attributes)
        username, *full_message = message.split()

        if full_message[0] in self.keywords:
            action, *rest_message = full_message
        else:
            action, rest_message = None, full_message

        parsed_message = {
            'username': username,
            'full_message': message,
            'action': action,
            'text': ' '.join(rest_message),
            'channel': 'text_channel',
        }

        msg = message_obj(**parsed_message)
        return msg

    def keyword_parser(self, msg):
        """Prepare and update Meeting attributes.

        Args:
            msg (Message): Conversation text.

        """
        if msg.action in self.keywords:
            if msg.action == '#startmeeting':
                self._started = True

            if '#endmeeting' in msg.action:
                self._started = False
                self.results['discussion'].append(msg.full_message)
                return

            if msg.action == '#topic':
                self._start_topic = msg.text
                self.results['topics'][self._start_topic] = {'discussion': [], 'info': [], }

            if msg.action == '#info':
                self._start_info = True

            if msg.action == '#action':
                self._start_action = True
                if msg.username not in self.results['actions']:
                    self.results['actions'][msg.username] = []
