from xter.commandlistener import CommandListener


class CommandDispatcher:
    def __init__(self):
        self.listeners = []

    def dispatch_command(self, command,task_parameters):
        for listener in self.listeners:
            if isinstance(listener, CommandListener):
                if command.name in listener.for_commands:
                   return listener.execute(command,task_parameters)
            else:
                return 2

    def add_listener(self, listener):
        self.listeners.append(listener)
