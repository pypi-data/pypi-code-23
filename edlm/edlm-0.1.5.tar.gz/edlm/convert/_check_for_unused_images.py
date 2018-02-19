# coding=utf-8
"""
Checks that all images that in this document media folder
are used throughout the document, otherwise issue a warning
"""
from pathlib import Path

import elib


def check_for_unused_images(ctx):
    """
    Checks that all images that in this document media folder
    are used throughout the document, otherwise issue a warning

    Args:
        ctx: Context
    """

    unused_images = set()
    if len(ctx.media_folders) > 1:
        ctx.debug('checking media path for unused pictures')
        for file in Path(ctx.media_folders[0]).iterdir():
            if file.name not in ctx.images_used:
                ctx.debug(f'checking that "{file}" is used')
                unused_images.add(str(file.absolute()))

        if unused_images:
            ctx.warning(f'unused files found:\n{elib.pretty_format(sorted(unused_images))}')
