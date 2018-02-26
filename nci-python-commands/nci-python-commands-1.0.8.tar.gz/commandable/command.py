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

import argparse
import inspect
import sys
import os


class Command:
    description = "No description"
    hidden = False

    def __init__(self, args=None):
        if args is None:
            args = []

        self.parser = argparse.ArgumentParser(
            prog="python " + sys.argv[0] + " " + str.lower(
                os.path.splitext(
                    os.path.basename(
                        inspect.getfile(self.__class__)))[0]
            ),
            description=self.command_description())
        self.parameters = None
        self.extra = []
        self.processed = False
        self._args = args

        self.requiredGroup = self.parser.add_argument_group('required named arguments')

    def __enter__(self):
        self.parameters, self.extra = self.parser.parse_known_args(self._args)

    def __exit__(self, *args):
        pass

    def register_argument(self,
                          *names: str,
                          description: str = "",
                          type: object = str,
                          default=None,
                          required=False,
                          **kwargs):
        if required:
            self.requiredGroup.add_argument(
                *names,
                default=default,
                type=type,
                help=description,
                **kwargs)

            return

        self.parser.add_argument(
            *names,
            default=default,
            type=type,
            help=description,
            **kwargs)

    def command(self, **kwargs):
        raise NotImplementedError("Command should implement method command()")

    def get(self, parameter):
        return getattr(self.parameters, parameter)

    @classmethod
    def command_description(cls):
        return cls.description
