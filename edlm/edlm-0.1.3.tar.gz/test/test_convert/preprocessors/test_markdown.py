# coding=utf-8


from pathlib import Path

from mockito import verifyStubbedInvocationsAreUsed, when

from edlm.convert import Context
from edlm.convert._preprocessor import _markdown


def test_markdown_preprocessor():
    ctx = Context()
    index_file = Path('./index.md')
    index_file.write_text('', encoding='utf8')
    ctx.index_file = index_file
    ctx.includes = []
    ctx.markdown_text = ''
    when(_markdown).process_aliases(ctx)
    when(_markdown).process_images(ctx)
    when(_markdown).process_references(ctx)
    _markdown.process_markdown(ctx)
    verifyStubbedInvocationsAreUsed()
