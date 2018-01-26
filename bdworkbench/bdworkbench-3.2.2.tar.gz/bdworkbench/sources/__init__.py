#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .sources_package import SourcesPackage

class Sources(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'sources',
                        'Commmands to deliver source files as part of catalog bundles.')

        ## Initialize the subcommands.
        SourcesPackage(config, inmemStore, self)

__all__ = ['Sources']
Command.register(Sources)
