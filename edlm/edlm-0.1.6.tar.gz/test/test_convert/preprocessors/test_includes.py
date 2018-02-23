# coding=utf-8
from pathlib import Path

from edlm.convert._preprocessor._markdown._images import process_images
from edlm.convert._preprocessor._markdown._include import Context, process_includes
from edlm.convert._preprocessor._markdown._references import process_references


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


def test_include_refs():
    ctx = Context()
    ctx.settings.references = {
        '//ref1': 'ref1, link1',
        '//ref2': 'ref2, link2',
    }
    ctx.source_folder = Path('.').absolute()
    ctx.markdown_text = '//ref1\n\n//include "include.md"'
    include = Path('include.md').absolute()
    include.write_text('//ref2')
    ctx.includes = [include]
    process_references(ctx)
    process_includes(ctx)
    assert ctx.markdown_text == '[ref1](link1)\n\n[ref2](link2)', ctx.markdown_text
    assert '\\href{link1}{ref1}' in ctx.latex_refs
    assert '\\href{link2}{ref2}' in ctx.latex_refs


def test_include_images():
    ctx = Context()
    source_folder = Path('.').absolute()
    source_media = Path(source_folder, 'media').absolute()
    source_media.mkdir()
    media1 = Path(source_media, 'media1.png').absolute()
    media2 = Path(source_media, 'media2.png').absolute()
    media3 = Path(source_media, 'media3.png').absolute()
    for media in (media1, media2, media3):
        media.touch()
    ctx.source_folder = Path('.').absolute()
    ctx.markdown_text = '![media1](media1.png)\n\n//include "include.md"'
    include = Path('include.md').absolute()
    include.write_text('![media2](media2.png)')
    ctx.includes = [include]
    ctx.media_folders = [source_media]
    process_images(ctx)
    process_includes(ctx)
    assert media1.name in ctx.images_used
    assert media2.name in ctx.images_used
    assert not media3.name in ctx.images_used


def test_include_external_images():
    ctx = Context()
    source_folder = Path('source').absolute()
    source_folder.mkdir()
    parent_folder = Path('parent').absolute()
    parent_folder.mkdir()
    source_media = Path(source_folder, 'media').absolute()
    source_media.mkdir()
    media1 = Path(source_media, 'media1.png').absolute()
    media2 = Path(source_media, 'media2.png').absolute()
    media3 = Path(source_media, 'media3.png').absolute()
    parent_media = Path(parent_folder, 'media').absolute()
    parent_media.mkdir()
    parent_media1 = Path(parent_media, 'parent_media.png').absolute()
    for media in (media1, media2, media3, parent_media1):
        media.touch()
    ctx.source_folder = source_folder
    ctx.media_folders = [source_media]
    ctx.markdown_text = '![media1](media1.png)\n\n//include "parent"'
    include = Path(parent_folder, 'index.md').absolute()
    include.write_text('![parent_media1](parent_media.png)')
    ctx.includes = [parent_folder]
    process_images(ctx)
    process_includes(ctx)
    assert ctx.markdown_text == f'![media1]({media1}){{width="Nonemm"}}\n\n' \
                                f'![parent_media1]({parent_media1}){{width="Nonemm"}}'
