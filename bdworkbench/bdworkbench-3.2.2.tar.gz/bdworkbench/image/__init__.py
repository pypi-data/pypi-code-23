#!/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.

from __future__ import print_function
from .. import Command

from .image_file import ImageFile
from .image_list import ImageList
from .image_build import ImageBuild
from .image_download import ImageDownload

class Image(Command):
    """

    """

    def __init__(self, wb, config, inmemStore, ):
        Command.__init__(self, wb, config, inmemStore, 'image',
                         'Container image management for the catalog entry.')

        ## Initialize the subcommands.
        ImageFile(config, inmemStore, self)
        ImageList(config, inmemStore, self)
        ImageBuild(config, inmemStore, self)
        ImageDownload(config, inmemStore, self)

Command.register(Image)
__all__ = ['Image']

