#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .appconfig_list import AppconfigList
from .appconfig_file import AppconfigFile
from .appconfig_init import AppconfigInitcode
from .appconfig_package import AppconfigPackage
from .appconfig_autogen import AppconfigAutogen
from .appconfig_download import AppconfigDownload

class Appconfig(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'appconfig',
                         'Appconfig package management for a catalog entry.')

        ## Initialize the subcommands.
        AppconfigList(config, inmemStore, self)
        AppconfigFile(config, inmemStore, self)
        AppconfigAutogen(config, inmemStore, self)
        AppconfigPackage(config, inmemStore, self)
        AppconfigInitcode(config, inmemStore, self)
        AppconfigDownload(config, inmemStore, self)

__all__ = ['Appconfig']
Command.register(Appconfig)
