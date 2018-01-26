#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .logo_file import LogoFile
from .logo_list import LogoList
from .logo_download import LogoDownload

class Logo(Command):
    """

    """

    def __init__(self, wb, config, inmemStore, ):
        Command.__init__(self, wb, config, inmemStore, 'logo',
                         'Container logo management for the catalog entry.')

        ## Initialize the subcommands.
        LogoFile(config, inmemStore, self)
        LogoList(config, inmemStore, self)
        LogoDownload(config, inmemStore, self)

__all__ = ['Logo']
Command.register(Logo)
