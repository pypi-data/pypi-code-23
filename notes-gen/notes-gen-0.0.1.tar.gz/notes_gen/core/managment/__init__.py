import sys
import pkgutil
import argparse

from notes_gen.core.loggers import ConsoleLogger
from notes_gen.core.managment import commands

# Default logger
logger = ConsoleLogger()


class CommandLineParser(object):
    '''Parse command from command line and execute the respective command
    '''

    _HELP_COMMAND = 'help'
    _HELP_MSG = '''

Try one of the following commands.

For help regarding subcommad use the following "[command] --help"

\t[Avaliable Command]

\t{command_list}

'''

    def _print_help(self):
        '''Print a help message
        '''
        commands_list = []

        # Get sub moduels list in core.managment.commands module
        for _, modname, _ in pkgutil.iter_modules(commands.__path__):
            commands_list.append(modname)

        # Print Help
        print(self._HELP_MSG.format(command_list='\n\t'.join(commands_list)))

    def _get_command(self, name):
        '''Import Command from the commands moudle
        '''
        command_class = None

        for importer, modname, _ in pkgutil.iter_modules(commands.__path__):
            modname = modname.lower()
            if modname == name:
                command_class = importer.find_module(modname).load_module().Command
                break

        return command_class

    def _parse_command_name(self):
        '''Parse subcommand from the command line
        '''
        # Check if a command is suppiled
        if len(sys.argv) < 2:
            self._print_help()
            sys.exit()

        # Return command
        return sys.argv[1].strip().lower()

    def execute(self):
        '''Call the subcommand as per the user
        '''
        # Get command name
        command_name = self._parse_command_name()

        # If command is help, then print help
        if command_name == self._HELP_MSG:
            self._print_help()
            sys.exit()

        # If command is not a valid subcommand then print help and exit
        command_class = self._get_command(command_name)
        if command_class is None:
            self._print_help()
            sys.exit()

        # Get Command
        command_object = command_class()

        # Parse commmand specific arguments
        parser = argparse.ArgumentParser(prog=command_name, description=command_object.description)
        command_object.add_arguments(parser)
        args = parser.parse_args(sys.argv[2:])

        # Execute Command
        command_object.execute(args)
