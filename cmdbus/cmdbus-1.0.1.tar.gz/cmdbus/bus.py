from cmdbus.command import Command


class Bus:
    def dispatch(self, command: Command):
        return command.handle()
