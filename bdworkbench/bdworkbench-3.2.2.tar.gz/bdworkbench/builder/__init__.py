#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .builder_org import BuilderOrg
from .builder_registry import BuilderRegistry


class Builder(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'builder',
                         'Collects information about the catalog entry\'s builder.')

        BuilderOrg(config, inmemStore, self)
        BuilderRegistry(config, inmemStore, self)

Command.register(Builder)
__all__ = ['Builder']
