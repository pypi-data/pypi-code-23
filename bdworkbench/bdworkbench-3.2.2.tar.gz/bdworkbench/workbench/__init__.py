#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .workbench_initapp import WorkbenchInitapp
from .workbench_clean import WorkbenchClean
from .workbench_version import WorkbenchVersion

class Workbench(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'workspace',
                         'Manages a workspace for developing an app for EPIC.')

        WorkbenchInitapp(config, inmemStore, self)
        WorkbenchClean(config, inmemStore, self)
        WorkbenchVersion(config, inmemStore, self)

Command.register(Workbench)
__all__ = ['Workbench']
