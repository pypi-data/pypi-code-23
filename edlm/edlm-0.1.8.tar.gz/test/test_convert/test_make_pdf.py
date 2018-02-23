# coding=utf-8

import typing
from pathlib import Path

import elib
import elib._run
import pytest
from mockito import verify, verifyStubbedInvocationsAreUsed, when

from edlm.convert import Context, _make_pdf
from edlm.external_tools import PANDOC


@pytest.mark.parametrize(
    'format_',
    list(_make_pdf.PAPER_FORMATS_WIDTH.keys())
)
def test_max_image_width(format_):
    ctx = Context()
    ctx.paper_size = format_
    _make_pdf._set_max_image_width(ctx)
    assert ctx.image_max_width == int(_make_pdf.PAPER_FORMATS_WIDTH[format_])


@pytest.mark.parametrize(
    'format_',
    ('A8', 'A9', 'B4', 'nil', '1')
)
def test_max_image_wrong_value(format_):
    ctx = Context()
    ctx.paper_size = format_
    with pytest.raises(ValueError):
        _make_pdf._set_max_image_width(ctx)


def test_remove_artifacts():
    for _ in range(30):
        Path(f'./__TMP{elib.custom_random.random_string()}').mkdir()
        Path(f'./tex2pdf.{elib.custom_random.random_string()}').mkdir()
    _make_pdf._remove_artifacts()
    assert not list(Path('.').iterdir())


def _get_standard_build_folder() -> typing.Tuple[Context, Path]:
    ctx = Context()
    pandoc = Path('pandoc')
    pandoc.touch()
    src_folder = Path('./test').absolute()
    src_folder.mkdir()
    ctx.source_folder = src_folder
    source_file = Path('./test/index.md')
    source_file.touch()
    ctx.source_file = source_file
    ctx.markdown_text = ''
    return ctx, pandoc


@pytest.mark.parametrize(
    'paper_size',
    (['a4'], ['a3', 'a5'], ['a3'])
)
def test_build_folder(paper_size):
    ctx, pandoc = _get_standard_build_folder()
    ctx.settings.papersize = paper_size
    ctx.media_folders = []
    when(_make_pdf).get_media_folders(...)
    when(_make_pdf).skip_file(...)
    when(_make_pdf).add_metadata_to_pdf(ctx)
    when(_make_pdf).get_template(...)
    when(_make_pdf).get_index_file(...)
    when(_make_pdf).get_settings(...)
    when(_make_pdf).process_markdown(...)
    when(_make_pdf).process_latex(...)

    when(PANDOC).get_exe().thenReturn(pandoc)
    when(elib).run(...).thenReturn(('out', 0))
    _make_pdf._build_folder(ctx)
    verifyStubbedInvocationsAreUsed()
    assert ctx.title == 'test'


def test_build_folder_skip():
    ctx, _ = _get_standard_build_folder()
    ctx.settings.papersize = ['a4']
    when(_make_pdf).get_media_folders(...)
    when(_make_pdf).skip_file(...).thenReturn(True)
    when(_make_pdf).get_template(...)
    when(_make_pdf).get_index_file(...)
    when(_make_pdf).get_settings(...)
    _make_pdf._build_folder(ctx)
    verifyStubbedInvocationsAreUsed()


def test_is_source_folder():
    assert _make_pdf._is_source_folder(Path('.')) is False
    Path('./index.md').touch()
    assert _make_pdf._is_source_folder(Path('.')) is True


def test_is_source_folder_is_file():
    file = Path('./file')
    file.touch()
    assert _make_pdf._is_source_folder(file) is False


def test_make_pdf_empty_folder():
    ctx = Context()
    when(_make_pdf)._build_folder(ctx)
    _make_pdf.make_pdf(ctx, Path('.'))
    verify(_make_pdf, times=0)._build_folder(ctx)


def test_make_pdf_document_folder():
    ctx = Context()
    Path('./index.md').touch()
    when(_make_pdf)._build_folder(ctx)
    _make_pdf.make_pdf(ctx, Path('.'))
    verify(_make_pdf, times=1)._build_folder(ctx)


def test_make_pdf_parent_folder():
    ctx = Context()
    for sub_folder in [
        Path('./sub1'),
        Path('./sub2'),
        Path('./sub3'),
        Path('./sub4'),
    ]:
        sub_folder.mkdir()
        Path(sub_folder, 'index.md').touch()
    Path('./sub5').mkdir()
    when(_make_pdf)._build_folder(ctx)
    _make_pdf.make_pdf(ctx, Path('.'))
    verify(_make_pdf, times=4)._build_folder(ctx)


def test_download_existing_file(caplog):
    file = Path('test').absolute()
    ctx = _make_pdf.Context()
    ctx.out_file = file
    when(elib.downloader).download(...).thenReturn(True)
    _make_pdf._download_existing_file(ctx)
    assert 'download successful' in caplog.text
    when(elib.downloader).download(...).thenReturn(False)
    _make_pdf._download_existing_file(ctx)
    assert 'download failed' in caplog.text


def test_download_existing_file_file_exists(caplog):
    file = Path('test').absolute()
    ctx = _make_pdf.Context()
    ctx.out_file = file
    file.touch()
    _make_pdf._download_existing_file(ctx)
    assert 'download failed' not in caplog.text
    assert 'download successful' not in caplog.text
