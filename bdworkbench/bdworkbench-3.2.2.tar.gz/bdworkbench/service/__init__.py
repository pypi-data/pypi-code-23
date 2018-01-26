#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .service_add import ServiceAdd
from .service_list import ServiceList
from .service_remove import ServiceRemove
#from .service_dependency import ServiceDependency

class Service(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'service',
                        'Service management for a catalog entry.')

        ## Initialize the subcommands.
        ServiceAdd(config, inmemStore, self)
        ServiceList(config, inmemStore, self)
        ServiceRemove(config, inmemStore, self)
        #ServiceDependency(config, inmemStore, self)

__all__ = ['Service']
Command.register(Service)
