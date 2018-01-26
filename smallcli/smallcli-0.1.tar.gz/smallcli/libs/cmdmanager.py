# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import argparse
import abc
from six import add_metaclass, text_type
import argparse
import re

from smallcli.utils import get_resource_classes, Singleton
from smallcli.commands.base import Command


@add_metaclass(abc.ABCMeta)
class CommandManager(Singleton, object):
    """Base class for commands
    """
    description = ""

    def __init__(self, path=None, prefix=None):
        # Load the Commands Subclasses
        self.cmdcls = get_resource_classes(path, prefix)
        self.commands = [c.__name__ for c in self.cmdcls]
        self.commands.append("help")

        # Building Help Commands
        self.helpstr = "Available Commands \n"
        self.helpstr += "****************************************************\n"
        for cls in self.cmdcls:
            self.helpstr += cls.__name__ + " -------" + cls.description + "\n"
        self.helpstr += "****************************************************\n"

    def helpfn(self, arg=None):
        arg = [str(a) for a in arg if a]
        print  arg
           
        if len(arg)>=1 and arg[0] in self.commands:
            result = "****************************************************\n"
            for cls in self.cmdcls:
                if self.isequal(str(arg[0]), str(cls.__name__)):
                    result+= cls.details + "\n"
            result += "****************************************************\n"
            return result
        return self.helpstr


    def list(self, filter="*"):
        # return the commands name
        res = []
        if filter == "*":
            return self.commands
        else:
            for cmd in self.commands:
                match = re.match(r'(%s)' % filter, cmd, re.M | re.I)
                if match:
                    res.append(cmd)
            return res

    def isequal(self, a, b):
        return a.upper() == b.upper()

    def execute(self, cmdname):
        # cmd may have mutliple parts  . first part is cmd, remaining parts are args
        cmd = cmdname.split()
        x = len(cmd)
        # No Command entered, user pressed enter
        if x == 0:
            return None
        # populating args for commands
        args = []
        if x != 0:
            args += cmd[1:]

        if cmd[0] in ["help", "Help", "HELP"]:
            return self.helpfn(args)
        # get the command object and execute call function
        for c in self.cmdcls:
            if self.isequal(str(cmd[0]), str(c.__name__)):
                return c()(args)
        return "Error : Command Not Found"


if __name__ == "__main__":
    cm = CommandManager()
    print cm.list("*")
    print cm.list("H")
    print cm.list("He")
    print cm.list("Pi")
    #print cm.execute("Help")
    #print get_resource_classes()
