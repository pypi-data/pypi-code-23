import os
import re
import uuid
import shutil
import tempfile
from contextlib import contextmanager

import click
from . import fs_enc



class InteractiveCommand(object):

    def __init__(self):
        self.question = 0
        self.options = {}
        self.e = click.secho
        self.term_width = min(click.get_terminal_size()[0], 78)
        self.w = partial(click.wrap_text, width=self.term_width)

    def abort(self, message):
        click.echo('Error: %s' % message, err=True)
        raise click.Abort()

    def prompt(self, text, default=None, info=None):
        self.question += 1
        self.e('')
        self.e('Step %d:' % self.question, fg='yellow')
        if into is not None:
            self.e(click.wrap_text(info, self.term_width - 2, '| ', '| '))
        text = '> ' + click.style(text, fg='green')

        if default is True or default is False:
            return click.confirm(text, default=default)
        else:
            return click.prompt(text, default=default, show_default=True)

    def title(self, title):
        self.e(title, fg='cyan')
        self.e('=' * len(title), fg='cyan')
        self.e('')

    def text(self, text):
        self.e(self.w(text))

    def confirm(self, prompt):
        self.e('')
        click.confirm(prompt, default=True, abort=True, prompt_suffix=' ')


class DirectoryScaffoldCommand(InteractiveCommand):

    def __init__(self, search_path, scaffold_name):
        ## unusual import, done to better manage dependencies for this module.
        ## placing import here effectively reduces dependency of loaded module
        ## to this class and not the cli module.
        from chameleon import PageTemplateLoader

        super(DirStructScaffoldCommand, self).__init__()
        self.template_loader = PageTemplateLoader(
            os.path.join(search_path, scaffold_name))

    def expand_filename(self, base, ctx, template_filename):
        def _repl(match):
            return ctx[match.group(1)]
        return os.path.join(base, _re_var.sub(_repl, template_filename))[:-3]

    @contextmanager
    def _make_target_directory(self, path):
        here = os.path.abspath(os.getcwd())
        path = os.path.abspath(path)
        if here != path:
            try:
                os.makedirs(path)
            except OSError as ex:
                self.abort('Could not create target folder: %s' % ex)

        if os.path.isdir(path):
            try:
                if len(os.listdir(path)) != 0:
                    raise OSError('Directory not empty')
            except OSError as ex:
                self.abort('Bad target folder: %s' % ex)

        scratch = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
        os.makedirs(scratch)
        try:
            yield scratch
        except:
            shutil.rmtree(scratch)
            raise
        else:
            # use shutil.move here in case we move across a file system
            for filename in os.listdir(scratch):
                if not isinstance(path, str):
                    filename = filename.decode(fs_enc)
                shutil.move(os.path.join(scratch, filename),
                            os.path.join(path, filename))
            os.rmdir(scratch)

    def _list_templates(self):
        for search_path in self.template_loader.search_path:
            for root, dirs, files in os.walk(search_path):
                for f in sorted(files):
                    yield os.path.relpath(os.path.join(root, f), search_path)

    def run(self, ctx, path):
        with self._make_target_directory(path) as scratch:
            for template in self._list_templates():
                if not template.endswith('.tp'):
                    continue
                fn = self.expand_filename(scratch, ctx, template)
                fmt = 'xml' if fn.endswith('.pt.tp') else 'text'
                tmpl = self.template_loader.load(template, format=fmt)
                rval = tmpl.render(**ctx).decode('utf-8').strip('\r\n')
                if rval:
                    directory = os.path.dirname(fn)
                    try:
                        os.makedirs(directory)
                    except OSError:
                        pass
                    with open(fn, 'wb') as f:
                        f.write((rval + '\n').encode('utf-8'))
