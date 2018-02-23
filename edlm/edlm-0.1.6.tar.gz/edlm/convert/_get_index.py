# coding=utf-8
"""
Gathers "index.md" file
"""

import elib

from ._context import Context


def get_index_file(ctx: Context):
    """
    Gathers "index.md" file
    """
    index_file = elib.path.ensure_file(ctx.source_folder, 'index.md')
    ctx.debug(f'index file: {index_file}')
    ctx.index_file = index_file
    ctx.markdown_text = ctx.index_file.read_text(encoding='utf8')
