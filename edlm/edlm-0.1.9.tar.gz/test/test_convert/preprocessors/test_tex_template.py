# coding=utf-8

from pathlib import Path

import pytest
from jinja2 import Environment, TemplateNotFound
from mockito import when

import edlm.convert._preprocessor._latex as latex
from edlm.convert import Context


def test_template_loader():
    ctx = Context()
    template = Path('./template.tex').absolute()
    template.write_text('moo', encoding='utf8')
    ctx.template_source = template
    env = Environment(autoescape=True)
    loader = latex.TexTemplateLoader(ctx)
    source, template_, reload = loader.get_source(env, 'template.tex')
    assert source == 'moo'
    assert template_ == template
    assert reload is False


def test_template_loader_no_template():
    ctx = Context()
    template = Path('./template.tex').absolute()
    ctx.template_source = template
    env = Environment(autoescape=True)
    loader = latex.TexTemplateLoader(ctx)
    with pytest.raises(TemplateNotFound):
        loader.get_source(env, 'template.tex')


def test_process_template_no_template():
    ctx = Context()
    template = Path('./template.tex').absolute()
    ctx.template_source = template
    with pytest.raises(FileNotFoundError):
        latex.process_latex(ctx)


def test_process_template_latex_error():
    ctx = Context()
    template = Path('./template.tex').absolute()
    ctx.template_source = template
    ctx.media_folders = []
    template.touch()
    when(latex.TexTemplateLoader).get_source(...).thenRaise(TemplateNotFound(ctx))
    ctx.template_source = template
    with pytest.raises(TemplateNotFound):
        latex.process_latex(ctx)


def test_process_template():
    ctx = Context()
    template = Path('./template.tex').absolute()
    template_out = Path('./out.tex').absolute()
    ctx.template_file = template_out
    ctx.template_source = template
    ctx.media_folders = []
    template.touch()
    ctx.template_source = template
    latex.process_latex(ctx)
    assert ctx.template_file.read_text(encoding='utf8') == ''
