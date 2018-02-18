# coding=utf-8

from pathlib import Path

from edlm.convert._get_includes import Context, get_includes


def test_no_includes():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    ctx.markdown_text = 'some text'
    get_includes(ctx)
    assert not ctx.includes


def test_local_includes():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    ctx.markdown_text = 'some text\n\n//include "include.md"'
    include = Path('include.md').absolute()
    include.write_text('plop', encoding='utf8')
    include2 = Path('include2.md').absolute()
    include2.write_text('plop', encoding='utf8')
    get_includes(ctx)
    assert ctx.includes == [include]


def test_external_includes():
    ctx = Context()
    source_folder = Path('./plop').absolute()
    source_folder.mkdir()
    ctx.source_folder = source_folder
    ctx.markdown_text = 'some text\n\n//include "some doc"'
    include_folder = Path('some doc').absolute()
    include_folder.mkdir()
    include = Path(include_folder, 'index.md').absolute()
    include.write_text('plop', encoding='utf8')
    include_folder2 = Path('some other doc').absolute()
    include_folder2.mkdir()
    include2 = Path(include_folder, 'index.md').absolute()
    include2.write_text('plop', encoding='utf8')
    get_includes(ctx)
    assert ctx.includes == [include_folder]
