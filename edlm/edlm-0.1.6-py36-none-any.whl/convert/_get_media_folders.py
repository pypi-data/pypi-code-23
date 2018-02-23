# coding=utf-8
"""
Gathers the media folders
"""

import elib

from ._context import Context


def get_media_folders(ctx: Context):
    """
    Gathers the media folders
    """
    ctx.info('gathering media folders')

    media_folders = []

    this_folder = ctx.source_folder
    while True:
        ctx.debug(f'traversing: "{this_folder}"')
        media_folder_candidate = elib.path.ensure_path(this_folder, 'media', must_exist=False).absolute()
        if media_folder_candidate.exists() and media_folder_candidate.is_dir():
            ctx.debug(f'media folder found: "{media_folder_candidate}"')
            media_folders.append(media_folder_candidate)
        if len(this_folder.parents) is 1:
            ctx.debug(f'reach mount point at: "{this_folder}"')
            break
        this_folder = this_folder.parent

    # if not media_folders:
    #     raise ConvertError('no media folder found', ctx)

    ctx.info(f'media folders:\n{elib.pretty_format(media_folders)}')
    ctx.media_folders = media_folders
