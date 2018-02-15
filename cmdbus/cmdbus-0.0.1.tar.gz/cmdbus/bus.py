from cmdbus.command import Command


class Bus:
    @staticmethod
    def dispatch(command: Command):
        command.handle()
