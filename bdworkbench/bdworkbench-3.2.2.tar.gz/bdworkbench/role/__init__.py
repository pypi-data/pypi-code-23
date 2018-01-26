#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .role_add import RoleAdd
from .role_list import RoleList
from .role_remove import RoleRemove

class Role(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'role',
                         'Role management for a catalog entry.')

        ## Initialize the subcommands.
        RoleAdd(config, inmemStore, self)
        RoleList(config, inmemStore, self)
        RoleRemove(config, inmemStore, self)

__all__ = ['Role']
Command.register(Role)
