# coding=utf-8
"""
Get templates folder
"""

from pathlib import Path

from . import Context


def get_template(ctx: Context):
    """
    Get templates folder
    """

    ctx.info('looking for template')

    ctx.template_source = None

    this_folder = ctx.source_folder
    while not ctx.template_source:
        ctx.debug(f'traversing: {this_folder}')
        file = Path(this_folder, 'template.tex').absolute()
        if file.exists() and file.is_file():
            ctx.template_source = file
        if len(this_folder.parents) is 1:
            raise FileNotFoundError('no "template.tex" file found', ctx)
        this_folder = this_folder.parent

    ctx.info(f'using template file: {ctx.template_source}')
