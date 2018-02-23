# coding=utf-8

from pathlib import Path

import pdfrw
from mockito import mock, verify, when

from edlm import __version__
from edlm.convert import _pdf_info


def test_get_document_hash():
    ctx = _pdf_info.Context()
    ctx.source_folder = Path('.')
    index_file = Path('index.md')
    index_file.write_text('dsfsdfsdfsdfsdf', encoding='utf8')
    template = Path('template.tex')
    template.write_text('sxdvxfgsfdsdf', encoding='utf8')
    dummy = Path('dummy')
    dummy.touch()
    settings = Path('settings.yml')
    settings.write_text('cxvsdfgqsdfqsdq', encoding='utf8')
    media = Path('./media')
    media.mkdir()
    pic = Path(media, 'pic')
    pic.write_text('sdvsdfsdfqazfqsdf', encoding='utf8')
    ctx.index_file = index_file
    ctx.template_source = template
    ctx.settings_files = [settings]
    ctx.media_folders = [media]
    include_dir = Path('include')
    include_dir.mkdir()
    include_file = Path(include_dir, 'include.md')
    include_file.write_text('sdfsdf', encoding='utf8')
    ctx.includes = [include_dir, include_file]
    hash_ = _pdf_info._get_document_hash(ctx)
    assert hash_ == _pdf_info._get_document_hash(ctx)
    index_file.write_text('sdfsfsaqzzdqscxdcg', encoding='utf8')
    dummy.write_text('sdfsdvcsdvxwdvsdf', encoding='utf8')
    assert hash_ != _pdf_info._get_document_hash(ctx)
    hash_ = _pdf_info._get_document_hash(ctx)
    assert hash_ == _pdf_info._get_document_hash(ctx)
    template.write_text('sdgfsdfqljkqslkjdh', encoding='utf8')
    dummy.write_text('sdfsdvcsdqsdqsdvxwdvsdf', encoding='utf8')
    assert hash_ != _pdf_info._get_document_hash(ctx)
    hash_ = _pdf_info._get_document_hash(ctx)
    assert hash_ == _pdf_info._get_document_hash(ctx)
    settings.write_text('sdgfsdfqljkqslkjdh', encoding='utf8')
    dummy.write_text('qsdqsdqdazazreqsdf', encoding='utf8')
    assert hash_ != _pdf_info._get_document_hash(ctx)
    hash_ = _pdf_info._get_document_hash(ctx)
    assert hash_ == _pdf_info._get_document_hash(ctx)
    pic.write_text('sdgfsdfqljkqslkjdh', encoding='utf8')
    dummy.write_text('qsddsdds', encoding='utf8')
    assert hash_ != _pdf_info._get_document_hash(ctx)
    hash_ = _pdf_info._get_document_hash(ctx)
    assert hash_ == _pdf_info._get_document_hash(ctx)
    include_file.write_text('wxcwxcmlml', encoding='utf8')
    assert hash_ != _pdf_info._get_document_hash(ctx)
    hash_ = _pdf_info._get_document_hash(ctx)
    assert hash_ == _pdf_info._get_document_hash(ctx)


def test_skip_file_doesnt_exist():
    ctx = _pdf_info.Context()
    ctx.out_file = Path('./test')
    assert not _pdf_info.skip_file(ctx)


def test_skip_file_should_skip(caplog):
    ctx = _pdf_info.Context()
    ctx.out_file = Path('./test')
    pdf = mock()
    pdf.Info = mock()
    pdf.Info.Creator = 'creator'
    pdf.Info.Producer = 'producer'
    Path('./test').touch()
    when(pdfrw).PdfReader(...).thenReturn(pdf)
    when(pdfrw.objects.pdfstring.PdfString).to_unicode(...) \
        .thenReturn('EDLM ' + __version__) \
        .thenReturn('EDLM hash')
    when(_pdf_info)._get_document_hash(...).thenReturn('hash')
    assert _pdf_info.skip_file(ctx)
    assert 'this document has not been modified, skipping it' in caplog.text


def _get_should_skip_context(hash_='EDLM hash', version=__version__) -> _pdf_info.Context:
    ctx = _pdf_info.Context()
    ctx.out_file = Path('./test')
    pdf = mock()
    pdf.Info = mock()
    pdf.Info.Creator = 'creator'
    pdf.Info.Producer = 'producer'
    Path('./test').touch()
    when(pdfrw).PdfReader(...).thenReturn(pdf)
    when(pdfrw.objects.pdfstring.PdfString).to_unicode(...) \
        .thenReturn('EDLM ' + version) \
        .thenReturn(hash_)
    when(_pdf_info)._get_document_hash(...).thenReturn('hash')
    return ctx


def test_skip_file_force_regen(caplog):
    ctx = _get_should_skip_context()
    ctx.regen = True
    assert not _pdf_info.skip_file(ctx)
    assert 'forcing re-generation of all documents anyway' in caplog.text


def test_skip_file_document_updated(caplog):
    ctx = _get_should_skip_context(hash_='EDLM not the hash')
    assert not _pdf_info.skip_file(ctx)
    assert 'document updated, regenerating' in caplog.text


def test_skip_file_wrong_version(caplog):
    ctx = _get_should_skip_context(version='other version')
    assert not _pdf_info.skip_file(ctx)
    assert 'document generated with an older version of EDLM, regenerating' in caplog.text


def test_add_metadata():
    ctx = _pdf_info.Context()
    ctx.out_file = Path('./test')
    Path('./test').touch()
    writer = mock()
    when(writer).write()
    trailer = mock()
    trailer.Info = mock()
    when(pdfrw).PdfReader(str(ctx.out_file.absolute())).thenReturn(trailer)
    when(pdfrw).PdfFileWriter(str(ctx.out_file.absolute()), trailer=trailer).thenReturn(writer)
    when(_pdf_info)._get_document_hash(...).thenReturn('hash')
    _pdf_info.add_metadata_to_pdf(ctx)
    verify(writer).write()
    assert trailer.Info.Creator == 'EDLM ' + __version__
    assert trailer.Info.Producer == 'EDLM hash'
