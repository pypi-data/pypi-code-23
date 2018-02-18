# coding=utf-8
"""
Processing of Markdown content
"""

from ..._context import Context
from ._aliases import process_aliases
from ._images import process_images
from ._references import process_references
from ._include import process_includes


def process_markdown(ctx: Context):
    """
    Processing of Markdown content
    """
    ctx.debug(f'processing markdown file: {ctx.index_file}')
    process_aliases(ctx)
    process_images(ctx)
    process_references(ctx)
    process_includes(ctx)
