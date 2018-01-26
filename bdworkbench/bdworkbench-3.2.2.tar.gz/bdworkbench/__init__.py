#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from abc import ABCMeta, abstractmethod

import argparse, copy

from .utils import isDebug
from .utils.misc import processArgs
from .version import __version__


class SubCommand(object):
    """

    """
    __metaclass__ = ABCMeta

    def __init__(self, config, inmemStore, cmdObj, subcmd):
        self.config = config
        self.inmemStore = inmemStore

        # Register this SubCommand with the parent Command.
        cmdObj.addSubcommand(subcmd, self)

    def setWorkbench(self, workbench):
        self.workbench = workbench

    @abstractmethod
    def getSubcmdDescripton(self):
        raise Exception("Function must be implemented.")

    @abstractmethod
    def populateParserArgs(self, subparser):
        raise Exception("Function must be implemented.")

    @abstractmethod
    def run(self, processedArgs):
        """
        The implementation of this method must return True on successful
        completion and False on a failure.
        """
        raise Exception("Function must be implemented.")

    @abstractmethod
    def complete(self, text, argsList):
        raise Exception("Function must be implemented.")

class Command(object):
    """

    """
    __metaclass__ = ABCMeta

    def __init__(self, workbench, config, inmemStore, cmd, desc):
        """

        """
        self.cmd = cmd
        self.config = config
        self.workbench = workbench
        self.inmemStore = inmemStore
        self.parser = argparse.ArgumentParser(prog=cmd, description=desc)
        self.subparsers = self.parser.add_subparsers(dest='subcmd',
                                                     title='Subcommands')
        self.subcommands = {}

    def addSubcommand(self, subcmd, subcmdObj):
        desc = subcmdObj.getSubcmdDescripton()
        parser_subcmd = self.subparsers.add_parser(subcmd, help=desc,
                                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subcmdObj.populateParserArgs(parser_subcmd)

        self.subcommands[subcmd] = subcmdObj
        subcmdObj.setWorkbench(self.workbench)

    def _split_line(self, line):
        return line.strip().split()

    def _invoke_subcmd_complete(self, splits, text):
        subcmd = splits.pop(0)
        try:
            subcmdObj = self.subcommands[subcmd]
            return getattr(subcmdObj, 'complete')(text, splits)
        except KeyError:
            raise Exception("Unknown subcommand: %s" % subcmd)

    def run(self, line):
        """
        """
        try:
            args = processArgs(self.parser, line)
        except Exception as e:
            print(e)
            return False

        if args is not None:
            subcmdObj = self.subcommands[args.subcmd]

            if isDebug():
                print("DEBUG: ", self.cmd, " args:", args)

            return subcmdObj.run(args)
        else:
            ## Failed to process arguments. If we are in the non-interactive
            ## session, we must fail now.
            if self.workbench.use_rawinput == False:
                return False ## don't continue

        return True ## okay to continue

    def help(self):
        """

        """
        self.parser.print_help()

    def complete(self, text, line, begidx, endidx):
        """

        """
        splits = self._split_line(line.strip())
        if (len(splits) < 2 and text == '') or (len(splits) == 2 and text != ''):
            completionOpts = copy.deepcopy(self.subcommands.keys())
            completionOpts.append('-h')
            return [x for x in completionOpts if x.startswith(text)]
        else:
            splits.pop(0)
            return self._invoke_subcmd_complete(splits, text)

from workbench import Workbench

__all__ = [ "Workbench", "__version__" ]
