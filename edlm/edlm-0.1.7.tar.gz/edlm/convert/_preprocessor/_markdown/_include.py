# coding=utf-8
"""
Replaces include directive with the actual markdown content
"""

from pathlib import Path

import elib

from . import Context


class Inclusion:
    """
    Dummy context for a file inclusion
    """
    sub_context: Context
    include_str: str
    markdown_source: Path
    parent_folder: Path


def _process_include(ctx: Context, inclusion: Inclusion):
    from . import process_markdown
    from ..._get_includes import get_includes
    from ..._get_media_folders import get_media_folders
    inclusion.sub_context.markdown_text = inclusion.markdown_source.read_text(encoding='utf8')
    inclusion.sub_context.index_file = inclusion.markdown_source
    inclusion.sub_context.includes = []
    get_includes(inclusion.sub_context)
    get_media_folders(inclusion.sub_context)
    process_markdown(inclusion.sub_context)
    ctx.markdown_text = ctx.markdown_text.replace(inclusion.include_str, inclusion.sub_context.markdown_text)
    if inclusion.sub_context.latex_refs:
        refs = set(inclusion.sub_context.latex_refs)
        refs.update(ctx.latex_refs)
        ctx.latex_refs = list(refs)


def _process_local_include(ctx: Context, inclusion: Inclusion):
    inclusion.include_str = f'//include "{inclusion.parent_folder.relative_to(ctx.source_folder)}"'
    inclusion.markdown_source = Path(ctx.source_folder, inclusion.parent_folder)
    _process_include(ctx, inclusion)
    if inclusion.sub_context.images_used:
        ctx.images_used.update(inclusion.sub_context.images_used)


def _process_external_include(ctx: Context, inclusion: Inclusion):
    inclusion.include_str = f'//include "{inclusion.parent_folder.relative_to(ctx.source_folder.parent)}"'
    inclusion.markdown_source = Path(inclusion.parent_folder, 'index.md')
    inclusion.sub_context.source_folder = inclusion.parent_folder
    _process_include(ctx, inclusion)


def _get_unprocessed_includes(ctx: Context):
    for line_nr, line in enumerate(ctx.markdown_text.split('\n')):
        if '//include' in line:
            ctx.unprocessed_includes.append(f'line {line_nr+1:05d}: {line}')


def process_includes(ctx: Context):
    """
    Replaces include directive with the actual markdown content

    Args:
        ctx: Context
    """
    ctx.unprocessed_includes = []
    for include in ctx.includes:
        inclusion = Inclusion()
        inclusion.sub_context = ctx.get_sub_context()
        inclusion.parent_folder = include
        if include.is_file():
            _process_local_include(ctx, inclusion)
        elif include.is_dir():  # pragma: no branch
            _process_external_include(ctx, inclusion)

    _get_unprocessed_includes(ctx)
    if ctx.unprocessed_includes:
        ctx.warning(f'there are unprocessed "//include" directives:\n{elib.pretty_format(ctx.unprocessed_includes)}')
