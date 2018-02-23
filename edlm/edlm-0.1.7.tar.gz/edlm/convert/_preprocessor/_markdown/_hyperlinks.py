# coding=utf-8
"""
Converts \ref into \\fullref
"""

from . import Context


def process_hyperlinks(ctx: Context):
    """
    Converts \ref into \\fullref
    """
    ctx.markdown_text = ctx.markdown_text.replace('\\ref', '\\fullref')
