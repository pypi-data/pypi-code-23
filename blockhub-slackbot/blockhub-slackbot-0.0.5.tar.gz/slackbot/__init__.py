from slackclient import SlackClient
import re
import time
from slackbot.helpers import listify
from slackbot.attachments import ResponseBuilder


MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


class Bot:
    """
    A base class for creating bots, simply create a method without __ in front. The bot will then parse the method name
    as the first word, and everything after it as arguments (see greet)
    """

    def __init__(self, token, delay=0.2, warn_channel='servers'):
        self.delay = delay
        self.__client = SlackClient(token)

        self.__client.rtm_connect(with_team_state=False)

        self.id = self.__client.api_call("auth.test")["user_id"]
        self.warn_channel = warn_channel
        self.cycle_registry = {}
        self.cyle = 0

    def __parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), listify(matches.group(2).strip())) if matches else (None, None)

    def __parse_command(self, events):
        if events:
            for event in events:
                if event['type'] == "message" and "subtype" not in event:
                    user_id, message = self.__parse_direct_mention(event["text"])
                    if user_id == self.id and message:
                        command = message[0]
                        args = message[1:]
                        # safety precaution to make sure private methods can never be accessed.
                        if '__' not in args:
                            try:
                                return getattr(self, command), args, event["channel"]
                            except AttributeError:
                                return getattr(self, 'help'), args, event["channel"]
        return None, None, None

    def __handle_command(self, method, args, channel):
        default_response = "Not sure what you mean. To list all commands, use: help"

        if not args:
            # multiple args can be returned, this ensures no iteration errors are caused.
            args = ([],)

        try:
            try:
                response, attachment = method()(args[0])
            except TypeError:
                response, attachment = method(args[0])
        except AttributeError:
            response, attachment = default_response, None

        if attachment:
            self.__client.api_call(
                "chat.postMessage",
                channel=channel,
                attachments=response
            )
        else:
            self.__client.api_call(
                "chat.postMessage",
                channel=channel,
                text=response or default_response
            )

    def __send_wrn(self, message, attachment, channel):
        if attachment:
            self.__client.api_call(
                "chat.postMessage",
                channel=channel,
                attachments=message,
            )

        else:
            self.__client.api_call(
                "chat.postMessage",
                channel=channel,
                text=message,
            )

    def start(self):
        method_list = [getattr(self, func) for func in dir(self) if callable(getattr(self, func)) and func.startswith("on_cycle")]

        for i in method_list:
            self.cycle_registry.update({i: 0})
        while True:
            command, args, channel = self.__parse_command(self.__client.rtm_read())
            if command:
                self.__handle_command(command, args, channel)

            for i in self.cycle_registry:
                if self.cycle_registry[i] == 0:
                    msg, attachment = i()()

                    if msg:
                        self.__send_wrn(msg, attachment, self.warn_channel)
                    self.cycle_registry[i] += 1

                else:
                    self.cycle_registry[i] += 1

                    if self.cycle_registry[i] == i().frequency:
                        self.cycle_registry[i] = 0

            time.sleep(self.delay)

    class greet:
        def __init__(self):
            self.desc = "When the sysadmin gets lonely checking the nodes, he can greet me."
            self.allowed_commands = []
            self.builder = ResponseBuilder()

        def __call__(self, args):
            self.builder.attachment = False
            self.builder.text = 'hello'
            return self.builder.extract()

    def help(self, arg=None):

        response = ResponseBuilder()
        response.help()

        callables = [f for f in dir(self) if callable(getattr(self, f)) and not f.startswith('_')
                     and not f.startswith('on_cycle') and not f.endswith('start')]
        response.fallback = 'These are my commands: {}'.format(callables)

        if not arg:
            for i in callables:
                response.add_field(title=i, short=True)

            response.pretext = 'These are my commands'
            return response.extract()

        if arg in callables:

            desc = getattr(self, arg)().desc
            commands = getattr(self, arg)().allowed_commands
            response.title = arg
            response.text = desc

            for i in commands:
                response.add_field(title=i, short=True)

            return response.extract()

        else:
            response.error()
            response.fallback = "Didn't get that option. These are my commands: {}".format(str(callables))
            response.text = "Didn't get that option. These are my commands:"
            for i in callables:
                response.add_field(title=i, short=True)
            return response.extract()
