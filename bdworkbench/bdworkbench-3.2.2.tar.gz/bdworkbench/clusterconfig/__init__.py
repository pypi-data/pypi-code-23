#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .clusterconfig_new import ClusterConfigurationNew
from .clusterconfig_list import ClusterConfigurationList
from .clusterconfig_assign import ClusterConfigurationAssign


class ClusterConfiguration(Command):
    """

    """

    def __init__(self, wb, config, inmemStore,):
        Command.__init__(self, wb, config, inmemStore, 'clusterconfig',
                         'Cluster configuration management for a catalog entry.')

        ## Initialize the subcommands
        ClusterConfigurationNew(config, inmemStore, self)
        ClusterConfigurationList(config, inmemStore, self)
        ClusterConfigurationAssign(config, inmemStore, self)

Command.register(ClusterConfiguration)
__all__ = ['clusterconfig']
