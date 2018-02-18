# coding=utf-8
"""
Manages PDF files metadata operations
"""

import hashlib
from pathlib import Path

import pdfrw
from pdfrw.objects import pdfstring

from edlm import __version__
from edlm.convert import Context


def _hash_folder(folder: Path):
    for item in folder.iterdir():
        assert isinstance(item, Path)
        if item.is_file() and item.suffix in ['.md', '.yml', '.tex']:
            yield item.read_bytes()
        elif item.is_dir():
            yield from _hash_folder(item)


def _iterate_over_data(ctx: Context):
    yield from _hash_folder(ctx.source_folder)
    for media_folder in ctx.media_folders:
        for file in media_folder.iterdir():
            yield file.read_bytes()
    for include in ctx.includes:
        if include.is_dir():
            yield from _hash_folder(include)


def _get_document_hash(ctx: Context) -> str:
    hash_ = hashlib.sha1()
    for data in _iterate_over_data(ctx):
        hash_.update(data)
    return hash_.hexdigest()


def skip_file(ctx: Context) -> bool:
    """
    Checks if a file should be skipped

    Tests for:
        - EDLM version
        - index.md
        - template.tex
        - media folders content

    Args:
        ctx: Context

    Returns: True if file should be skipped

    """
    if ctx.out_file.exists():
        pdf = pdfrw.PdfReader(str(ctx.out_file.absolute()))
        creator = pdfstring.PdfString.to_unicode(pdf.Info.Creator)
        if creator != 'EDLM ' + __version__:
            ctx.info('document generated with an older version of EDLM, regenerating')
            return False
        producer = pdfstring.PdfString.to_unicode(pdf.Info.Producer)
        if producer != 'EDLM ' + _get_document_hash(ctx):
            ctx.info('document updated, regenerating')
            return False
        ctx.info('this document has not been modified, skipping it')
        if ctx.regen:
            ctx.info('forcing re-generation of all documents anyway')
            return False

        return True

    return False


def add_metadata_to_pdf(ctx: Context):
    """
    Adds metadata about EDLM version and source files after
    PDF create

    Args:
        ctx: Context
    """
    out_file = str(ctx.out_file.absolute())
    trailer = pdfrw.PdfReader(out_file)
    trailer.Info.Creator = 'EDLM ' + __version__
    trailer.Info.Producer = 'EDLM ' + _get_document_hash(ctx)
    pdfrw.PdfFileWriter(out_file, trailer=trailer).write()
