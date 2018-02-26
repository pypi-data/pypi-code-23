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

import importlib
import pkgutil

from commandable import Command


class Help(Command):
    description = "Shows a list of all available commands"

    def __init__(self, args=None):
        super().__init__(args)

    def command(self, **kwargs):
        if "called" in kwargs and kwargs["called"] != str.lower(self.__class__.__name__):
            print("Could not find command `" + kwargs["called"] + "` in [" + ", ".join(kwargs["namespaces"]) + "]\n")
        else:
            print("\nList of available commands:")

        # List all available commands
        for namespace in kwargs["namespaces"]:
            commands = importlib.import_module(namespace)

            for importer, modname, ispkg in pkgutil.iter_modules(commands.__path__):
                command_module = importlib.import_module(namespace + "." + str.lower(modname))
                cmd = getattr(command_module, ''.join(word.capitalize() for word in modname.split("_")))
                instance = cmd()

                if isinstance(instance, Command) and cmd.hidden is False:
                    print("({}) \033[1m{}\033[0m - {}".format(namespace, modname, cmd.description))

        print("\n")
