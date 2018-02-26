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

import os
from confload import Config

from commandable import Command, CommandLoader


class CreateCommand(Command):
    description = "Generates an empty command"

    template = """from commandable import Command


class {Name}(Command):
    description = "{Description}"

    def __init__(self, args=None):
        super().__init__(args)

    def command(self, **kwargs):
        # Your command logic
        pass
"""

    def __init__(self, args=None):
        super().__init__(args)

    def list_options(self, namespaces):
        print("Please select a namespace or create a new one:")
        print("0) Create namespace")

        i = 0
        if namespaces is not None and len(namespaces) > 0:
            for namespace in list(namespaces.values()):
                i += 1
                print("{}) {}".format(i, namespace))

        print("")

        valid = False
        choice = -1
        while not valid:
            choice = int(input("Select (number): "))

            valid = 0 <= choice <= i
            if not valid:
                print("Please select an option between 0 and {}".format(i))

        return choice

    def create_namespace(self):
        """
        Creates a valid namespace to host commands
        """
        print("\nCreating namespace...")

        name = input(" - name (default = commands): ") or "commands"
        path = "./{}".format(name.replace(".", "/")).lower()

        os.makedirs(path, exist_ok=True)

        init_path = os.path.join(path, "__init__.py")
        if not os.path.isfile(init_path):
            open(init_path, 'w+').close()

        return name, path

    def create_command(self, namespace):
        print("Creating command in {}".format(namespace))

        while True:
            command_name = input(" - Command name ([a-zA-Z]): ")
            file_name = "{}.py".format(CommandLoader.to_underscore(command_name))
            file_path = os.path.join("./{}".format(namespace.replace(".", "/")), file_name)

            if os.path.isfile(file_path):
                print("Command name already exists, please select another name...")
                continue

            command_description = input(" - Description ([a-zA-Z ]): ")

            break

        content = self.template.format(
            **{
                "Name": command_name,
                "Description": command_description
            }
        )

        f = open(file_path, 'w+')
        f.write(content)
        f.close()

    def register_namespace(self, name, namespace):
        r = open('config.yml', 'r').readlines()
        w = open('config.yml', 'w')
        appended = False
        for line in r:
            w.write(line)
            if 'Commands:' in line:
                appended = True
                w.write("  \"{}\": {}\n".format(name, namespace))

        if not appended:
            w.write("Commands: \n")
            w.write("  \"{}\": {}\n".format(name, namespace))

        w.close()

    def command(self, **kwargs):
        namespaces = Config.get("Commands") or {}

        choice = self.list_options(namespaces)

        if choice == 0:
            namespace = self.create_namespace()
            namespaces[namespace[0]] = namespace[1]

            self.register_namespace(namespace[0], namespace[1].replace("./", "").replace("/", "."))

            choice = 0

        self.create_command(list(namespaces.values())[choice - 1])


