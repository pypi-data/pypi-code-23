# coding=utf-8
"""
Gathers settings
"""

from pathlib import Path

import elib
import yaml

from ._context import Context
from ._exc import ConvertError
from ._settings import Settings


def get_settings(ctx: Context):
    """
    Gathers settings
    """
    ctx.info('reading settings')

    ctx.settings = Settings()
    ctx.settings_files = []

    this_folder = ctx.source_folder
    while True:
        ctx.debug(f'traversing: {this_folder}')
        file = Path(this_folder, 'settings.yml')
        if file.exists() and file.is_file():
            ctx.debug(f'settings file found: {file}')
            ctx.settings_files.append(file)
        if len(this_folder.parents) is 1:
            ctx.debug(f'reach mount point at: "{this_folder}"')
            break
        this_folder = this_folder.parent

    if not ctx.settings_files:
        raise ConvertError('no "settings.yml" file found', ctx)

    for file in reversed(ctx.settings_files):
        if not file.read_text(encoding='utf8'):
            raise ConvertError(f'empty "settings.yml": {file.absolute()}', ctx)
        with open(file) as stream:
            these_settings = yaml.load(stream)
            ctx.debug(f'content of "{file}": {elib.pretty_format(these_settings)}')
        ctx.settings.update(these_settings)

    ctx.debug(f'settings files:\n{elib.pretty_format(ctx.settings_files)}')
    ctx.debug(f'settings:\n{elib.pretty_format(ctx.settings)}')
