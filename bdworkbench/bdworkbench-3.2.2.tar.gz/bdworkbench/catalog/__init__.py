#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .catalog_new import CatalogNew
from .catalog_save import CatalogSave
from .catalog_load import CatalogLoad
from .catalog_modify import CatalogModify
from .catalog_package import CatalogPackage

class Catalog(Command):
    """

    """

    def __init__(self, wb, config, inmemStore):
        Command.__init__(self, wb, config, inmemStore, 'catalog',
                         'Catalog entry management.')

        ## Initialize the subcommands.
        CatalogNew(config, inmemStore, self)
        CatalogSave(config, inmemStore, self)
        CatalogLoad(config, inmemStore, self)
        CatalogModify(config, inmemStore, self)
        CatalogPackage(config, inmemStore, self)

__all__ = ['Catalog']
Command.register(Catalog)
