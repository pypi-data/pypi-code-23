#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .baseimg_init import BaseimgInit

class Baseimg(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'baseimg',
                        '')

        ## Initialize the subcommands.
        BaseimgInit(config, inmemStore, self)

__all__ = ['Baseimg']
Command.register(Baseimg)
