# coding=utf-8
from pathlib import Path

from edlm.convert._preprocessor._markdown._include import Context, process_includes


def test_no_include():
    ctx = Context()
    ctx.markdown_text = 'some text'
    ctx.includes = []
    process_includes(ctx)
    assert ctx.markdown_text == 'some text'


def test_local_include():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    ctx.markdown_text = 'some text\n\n//include "include.md"'
    include = Path('include.md').absolute()
    include.write_text('some other text')
    ctx.includes = [include]
    process_includes(ctx)
    assert ctx.markdown_text == 'some text\n\nsome other text'


def test_unprocessed_include(caplog):
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    ctx.markdown_text = 'some text\n\n//include "include.md"\n\n//include "nope.md"'
    include = Path('include.md').absolute()
    include.write_text('some other text')
    ctx.includes = [include]
    process_includes(ctx)
    assert ctx.markdown_text == 'some text\n\nsome other text\n\n//include "nope.md"'
    assert 'there are unprocessed "//include" directives:' in caplog.text
    assert ctx.unprocessed_includes == ['line 00005: //include "nope.md"']
