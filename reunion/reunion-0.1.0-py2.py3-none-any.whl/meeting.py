from collections import namedtuple

class Meeting:

    def __init__(self):
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
            '#endmeeting',
        ]

        self._started = False
        self._start_topic = None
        self._start_action = None

    def parse(self, message):

        msg = self.message_parser(message)
        self.keyword_parser(msg)

        if self._started:
            self.results['discussion'].append(msg.full_message)

            if msg.username not in self.results['users']:
                self.results['users'][msg.username] = {
                    'actions': [],
                    'count': 0,
                    'messages': [],
                }

            self.results['users'][msg.username]['count'] += 1
            self.results['users'][msg.username]['messages'].append(msg.text)

            if self._start_topic and not msg.action:
                self.results['topics'][self._start_topic].append(msg.full_message)

            if self._start_action:
                self.results['actions'][msg.username].append(msg.text)
                self.results['users'][msg.username]['actions'].append(msg.text)

        self._start_action = False

    def message_parser(self, message):
        attributes = [
            'username',
            'full_message',
            'action',
            'text',
            'channel',
        ]

        Message = namedtuple('Message', attributes)
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

        msg = Message(**parsed_message)
        return msg

    def keyword_parser(self, msg):
        if msg.action in self.keywords:
            if '#startmeeting' == msg.action:
                self._started = True

            if '#endmeeting' in msg.action:
                self._started = False
                self.results['discussion'].append(msg.full_message)
                return

            if '#topic' == msg.action:
                self._start_topic = msg.text
                self.results['topics'][self._start_topic] = []

            if '#action' == msg.action:
                self._start_action = True
                if msg.username not in self.results['actions']:
                    self.results['actions'][msg.username] = []
