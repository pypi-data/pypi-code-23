#!/usr/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from __future__ import with_statement

import os, sys, cmd
from role import Role
from logo import Logo
from image import Image
from baseimg import Baseimg
from builder import Builder
from catalog import Catalog
from service import Service
from sources import Sources
from appconfig import Appconfig
from workbench import Workbench
from clusterconfig import ClusterConfiguration

from inmem_store import InmemStore
from utils import isDebug
from utils.config import WBConfig
from utils.misc import calculateAndValidateDockerVersion
from constants import BDS_WB_VERSION

__all__ = ['BDwb']

def appendLine(retline, newline):
    if retline == '':
        return newline
    else:
        return retline + " " + newline

class Batchfile(file):
    def __init__(self, filepath):
        with open(filepath, 'r') as f:
            self.lines = f.readlines()

    def close(self):
        return

    def readline(self):
        haveLine = False
        retLine = ''

        while not haveLine:
            if len(self.lines) == 0:
                return retLine
            else:
                line = self.lines.pop(0).rstrip('\r\n').strip()

            if (line == '') or line.startswith('#'):
                continue

            if line.endswith('\\'):
                line = line.rstrip('\\').strip()
                retLine = appendLine(retLine, line)
                haveLine = False
                continue
            else:
                retLine = appendLine(retLine, line)
                haveLine = True

        return retLine

class BDwb(cmd.Cmd):

    def __init__(self, instr=None, batchfile=None):
        self.config = WBConfig()
        self.batchfile = batchfile
        self.inmemStore = InmemStore()

        self.commands = {
                'role'    : Role(self, self.config, self.inmemStore),
                'logo'    : Logo(self, self.config, self.inmemStore),
                'image'   : Image(self, self.config, self.inmemStore),
                'baseimg' : Baseimg(self, self.config, self.inmemStore),
                'builder' : Builder(self, self.config, self.inmemStore),
                'catalog' : Catalog(self, self.config, self.inmemStore),
                'service' : Service(self, self.config, self.inmemStore),
                'sources' : Sources(self, self.config, self.inmemStore),
                'appconfig' : Appconfig(self, self.config, self.inmemStore),
                'workbench' : Workbench(self, self.config, self.inmemStore),
                'clusterconfig' : ClusterConfiguration(self, self.config, self.inmemStore)
        }

        self.ruler = '_'
        defIntro = "BlueData workbench version %s.\n" %(BDS_WB_VERSION)
        if self.batchfile:
            self.intro = defIntro + "Executing in non-interative mode."
            self.prompt = ''
            self.use_rawinput = False
            cmd.Cmd.__init__(self, stdin=Batchfile(self.batchfile))
        else:
            self.intro = defIntro + "Executing in interactive mode."
            self.prompt = 'bdwb> '
            self.use_rawinput = True
            cmd.Cmd.__init__(self)

        if instr != None:
            sys.exit(not self.onecmd(instr))

        if not calculateAndValidateDockerVersion(self.inmemStore):
            sys.exit(1)

    def emptyline(self):
        """
        Override this method so we don't automatically execute the previous cmd.
        """
        # do nothing.
        return

    def precmd(self, line):
        """
        This overridden method added for convienience when the user executes
        help. Normally for a subcommand help, the user must do the following:

            bdwb> catalog new -h

        instead, this override lets them do the following:

            bdwb> help catalog new

        The previous cmd will still work if the user happens to use it.
        """
        splits = line.split()

        if (len(splits) > 1) and splits[0] == 'help':
            if not (splits[1] == 'EOF' or splits[1] == 'exit'):
                return ' '.join(splits[1:] + ['-h'])
        else:
            if isDebug():
                print("EXECUTING:", line)

        return line

    def postcmd(self, cont, line):
        """
        This overridden method will stop the command loop depending on the return
        status of the command executed. This check only applies when executing
        in batch mode.
        """
        if cont == False:
            print("\n", "ERROR: Instruction failed: ", line, sep='')
            if self.use_rawinput == False:
                return True ## stop?

        return False ## stop?

    # ##############################################################
    # #         Use '!' to execute normal shell cmds               #
    # ##############################################################
    # def do_shell(self, line):
    #     output = os.popen(line).read()
    #     print(output)
    #     self.last_output = output

    ##############################################################
    #         workbench commad                                   #
    ##############################################################
    def do_workbench(self, line):
        return self.commands['workbench'].run(line)

    def help_workbench(self):
        self.commands['workbench'].help()

    ##############################################################
    #         builder commad                                     #
    ##############################################################
    def do_builder(self, line):
        return self.commands['builder'].run(line)

    def help_builder(self):
        self.commands['builder'].help()

    ##############################################################
    #         catalog commad                                     #
    ##############################################################
    def do_catalog(self, line):
        return self.commands['catalog'].run(line)

    def help_catalog(self):
        self.commands['catalog'].help()

    ##############################################################
    #         role commad                                        #
    ##############################################################
    def do_role(self, line):
        return self.commands['role'].run(line)

    def help_role(self):
        self.commands['role'].help()

    ##############################################################
    #         role commad                                        #
    ##############################################################
    def do_logo(self, line):
        return self.commands['logo'].run(line)

    def help_logo(self):
        self.commands['logo'].help()

    ##############################################################
    #         image commad                                       #
    ##############################################################
    def do_image(self, line):
        return self.commands['image'].run(line)

    def help_image(self):
        self.commands['image'].help()

    ##############################################################
    #         Base image commad                                  #
    ##############################################################
    def do_baseimg(self, line):
        return self.commands['baseimg'].run(line)

    def help_baseimg(self):
        self.commands['baseimg'].help()

    ##############################################################
    #         appconfig commad                                   #
    ##############################################################
    def do_appconfig(self, line):
        return self.commands['appconfig'].run(line)

    def help_appconfig(self):
        self.commands['appconfig'].help()

    ##############################################################
    #         service commands                                   #
    ##############################################################
    def do_service(self, line):
        return self.commands['service'].run(line)

    def help_service(self):
        self.commands['service'].help()

    ##############################################################
    #         sources commands                                   #
    ##############################################################
    def do_sources(self, line):
        return self.commands['sources'].run(line)

    def help_sources(self):
        self.commands['sources'].help()

    ##############################################################
    #         configuration commands                             #
    ##############################################################
    def do_clusterconfig(self, line):
        return self.commands['clusterconfig'].run(line)

    def help_clusterconfig(self):
        self.commands['clusterconfig'].help()

    ##############################################################
    #       default complete function                            #
    ##############################################################
    def completedefault(self, *ignored):
        (text, line, begidx, endidx) = ignored
        command = line.strip().split()[0]
        if self.commands.has_key(command):
            return self.commands[command].complete(text, line, begidx, endidx)
        else:
            return cmd.Cmd.completedefault(self, ignored)


    ##############################################################
    #                Exit the interactive shell                  #
    ##############################################################
    def do_exit(self, line):
        print("\n")
        sys.exit(0)

    def do_EOF(self, line):
        return self.do_exit(line)

    def help_exit(self):
        print('\n'.join(["exit | Ctrl+D", "\tExits the interactive shell."]))

    def help_EOF(self):
        self.help_exit()
