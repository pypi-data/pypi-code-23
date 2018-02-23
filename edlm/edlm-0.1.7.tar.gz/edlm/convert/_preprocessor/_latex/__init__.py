# coding=utf-8
"""
Processes Latex template
"""
import elib
from jinja2 import BaseLoader, Environment, TemplateNotFound

from ... import Context


class TexTemplateLoader(BaseLoader):
    """
    Loads the template for Jinja2
    """

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def get_source(self, environment, template):
        # noinspection SpellCheckingInspection
        """
        Get the template source, filename and reload helper for a template.
        It's passed the environment and template name and has to return a
        tuple in the form ``(source, filename, uptodate)`` or raise a
        `TemplateNotFound` error if it can't locate the template.

        The source part of the returned tuple must be the source of the
        template as unicode string or a ASCII bytestring.  The filename should
        be the name of the file on the filesystem if it was loaded from there,
        otherwise `None`.  The filename is used by python for the tracebacks
        if no loader extension is used.

        The last item in the tuple is the `uptodate` function.  If auto
        reloading is enabled it's always called to check if the template
        changed.  No arguments are passed so the function must store the
        old state somewhere (for example in a closure).  If it returns `False`
        the template will be reloaded.
        """
        self.ctx.debug(f'environment: {elib.pretty_format(environment)}')
        self.ctx.debug(f'template: {template}')
        if not self.ctx.template_source.exists():
            raise TemplateNotFound(str(self.ctx.template_source))
        source = self.ctx.template_source.read_text(encoding='utf8')
        # "False" here means always reload the template
        return source, self.ctx.template_source.absolute(), False


def _get_jinja_env(ctx: Context):
    return Environment(
        block_start_string=r'\BLOCK{',
        block_end_string=r'}',
        variable_start_string=r'\VAR{',
        variable_end_string=r'}',
        comment_start_string=r'\#{',
        comment_end_string=r'}',
        line_statement_prefix=r'%%',
        line_comment_prefix=r'%#',
        trim_blocks=True,
        autoescape=False,
        loader=TexTemplateLoader(ctx)
    )


def process_latex(ctx: Context):
    """
    Processes the Tex template

    Adds path the media folders
    """
    ctx.debug(f'processing Tex template file: {ctx.template_source}')

    try:
        elib.path.ensure_file(ctx.template_source)
    except FileNotFoundError:
        ctx.error(f'LaTeX template not found: "{ctx.template_source}"')
        raise

    jinja_env = _get_jinja_env(ctx)

    media_folders = [folder.absolute() for folder in ctx.media_folders]
    media_folders = [str(folder).replace('\\', '/') for folder in media_folders]
    media_folders = ''.join(f'{{{folder}/}}' for folder in media_folders)
    ctx.debug(f'adding media folders to template: {media_folders}')
    try:
        template = jinja_env.get_template(ctx.template_source.name)
        ctx.template_file.write_text(template.render(**locals()), encoding='utf8')
    except TemplateNotFound:
        ctx.error(f'template not found: {ctx.template_source}')
        raise
