import parse
import asyncio


class Dispatcher(object):
    """Class that recognizes commands and calls the corresponding functions.

    Parameters
    ----------
    client : discord.Client
        The Discord API to use.
    """
    def __init__(self, client):
        self.client = client
        client.event(self.on_message)
        self.commands = {}

    def register(self, syntax, regex):
        """Decorator to register functions as commands.

        Parameters
        ----------
        syntax : string
            The syntax string for help purposes.
        regex : string
            The regular expression that represents the syntax of the command.
        """
        def decorator(func):
            self.commands[regex] = (func, syntax)
            return func

        return decorator

    async def on_message(self, message):
        c = message.content
        for regex in self.commands:
           args = parse.parse(c, regex)
           if args:
               f = self.commands[regex][0]
               await f(args, message)
               break
