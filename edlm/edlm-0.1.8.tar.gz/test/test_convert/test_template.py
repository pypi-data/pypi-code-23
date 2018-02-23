# coding=utf-8

from pathlib import Path

import pytest

from edlm.convert import Context
from edlm.convert import _get_template as template


def test_no_template():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    with pytest.raises(FileNotFoundError):
        template.get_template(ctx)


def test_simple_template():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    template_file = Path('./template.tex').absolute()
    template_file.touch()
    template.get_template(ctx)
    assert ctx.template_source == template_file


def test_multiple_template():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()

    sub1 = Path('./sub1').absolute()
    sub1.mkdir()
    template_file1 = Path(sub1, 'template.tex').absolute()
    template_file1.touch()
    sub2 = Path(sub1, 'sub2').absolute()
    sub2.mkdir()
    template_file2 = Path(sub2, 'template.tex').absolute()
    template_file2.touch()
    sub3 = Path(sub2, 'sub3').absolute()
    sub3.mkdir()
    template_file3 = Path(sub3, 'template.tex').absolute()
    template_file3.touch()

    ctx.source_folder = Path(sub3).absolute()

    template.get_template(ctx)
    assert ctx.template_source == template_file3

    template_file3.unlink()

    template.get_template(ctx)
    assert ctx.template_source == template_file2

    template_file2.unlink()

    template.get_template(ctx)
    assert ctx.template_source == template_file1
