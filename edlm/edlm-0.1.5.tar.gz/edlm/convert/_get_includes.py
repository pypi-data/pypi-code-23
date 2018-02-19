# coding=utf-8
"""
Gather the includes that are use throughout the document
"""

import typing
from pathlib import Path

import elib

from . import Context


def _gather_indices(folder: Path) -> typing.Iterator[Path]:
    for item in folder.iterdir():
        assert isinstance(item, Path)
        if item.is_file() and not item.name == 'index.md' and item.name.endswith('.md'):
            yield item.absolute()


def _gather_external_includes(ctx: Context) -> typing.Iterator[Path]:
    for item in ctx.source_folder.parent.iterdir():
        assert isinstance(item, Path)
        if item.is_dir() and Path(item, 'index.md').exists():
            yield item.absolute()


def _process_own_includes(ctx: Context):
    for include in _gather_indices(ctx.source_folder):
        relative_include = include.relative_to(ctx.source_folder)
        if f'//include "{relative_include}"' in ctx.markdown_text:
            ctx.includes.append(include)


def _process_external_includes(ctx: Context):
    for include in _gather_external_includes(ctx):
        relative_include = include.relative_to(ctx.source_folder.parent)
        if f'//include "{relative_include}"' in ctx.markdown_text:
            ctx.includes.append(include)


def get_includes(ctx: Context):
    """
    Gather the includes that are use throughout the document

    Args:
        ctx: Context
    """
    ctx.includes = []
    _process_own_includes(ctx)
    _process_external_includes(ctx)
    if ctx.includes:
        ctx.info(f'includes:\n{elib.pretty_format(ctx.includes)}')
