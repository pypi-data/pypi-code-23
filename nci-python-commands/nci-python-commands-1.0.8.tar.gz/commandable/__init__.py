# Copyright 2017 NEWCRAFT GROUP B.V.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re
import sys
import os
import importlib
from modulefinder import Module
from commandable.command import Command
from commandable.commands.help import Help


class CommandLoader:
    """
    A basic command loader

    Parameters
    ----------
    namespaces: list
        A list of namespaces to accept commands from
    arguments: dict, optional
        The arguments to pass on to the command
    """

    def __init__(self, namespaces=None, arguments=None):
        if namespaces is None:
            namespaces = []

        if isinstance(namespaces, str):
            namespaces = [namespaces]

        namespaces += ["commandable.commands"]

        self.arguments = arguments or sys.argv[:]

        self.prog_name = os.path.basename(self.arguments[0])
        self.command = self.arguments[1] if len(self.arguments) > 1 else "help"
        self.namespaces = namespaces

        self.arguments = self.arguments[2:]

        self.execute(self.command)

    def execute(self, name):
        """
        Parameters
        ----------
        name : str
            The command to execute
        """
        namespaces = self.namespaces[:]

        instance = None
        while len(namespaces) > 0:
            instance = self.load_command(name, namespaces.pop())
            if instance is not None:
                break

        if instance is None:
            self.load_command("help", "commandable.commands", called=name)

    @staticmethod
    def to_camelcase(name):
        """
        Parameters
        ----------
        name : str
            The string to convert to camelcase formatting

        Returns
        -------
        str
            Converted name string from underscore to camel case
        """
        return ''.join(word.capitalize() or '_' for word in name.split("_"))

    @staticmethod
    def to_underscore(name):
        """
        Parameters
        ----------
        name : str
            The string to convert to underscore formatting

        Returns
        -------
            Converted name string from camel case to underscore
        """

        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def load_command(self, name, namespace, **kwargs):
        """
        Parameters
        ----------
        name : str
            The name of the commmand
        namespace : str
            A string representation of the namespace wherin the command is located (Example: commandable.commands)
        kwargs :
            A dictionary to pass to the command as arguments.
        """
        kwargs["namespaces"] = self.namespaces

        try:
            command_module: Module = importlib.import_module(namespace + "." + str.lower(name))
        except ModuleNotFoundError:
            return None

        cmd: Command = getattr(command_module, self.to_camelcase(name))(self.arguments)

        if isinstance(cmd, Command):
            with cmd:
                cmd.command(**kwargs)
        else:
            return None

        return cmd
