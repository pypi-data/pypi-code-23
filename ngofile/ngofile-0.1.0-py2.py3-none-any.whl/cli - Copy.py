# -*- coding: utf-8 -*-
"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mngoproject` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``ngoproject.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``ngoproject.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import gettext
import logging
from builtins import str

import click

from ngoproject import File
from ngoproject import Project
from ngoproject import PythonEnvironment
from ngoproject import ToxEnvironment
from ngoproject._project import TEMPLATE_CHOICES_DICT

_ = gettext.gettext

logging.basicConfig(level=logging.WARNING)


@click.group()
@click.option('--name', default=None, type=str, help=_('name of project'))
@click.pass_context
def project_cli(ctx, name):
    prj = Project(name)
    click.echo('Project %s' % prj.name)
    click.echo('in folder : %s' % click.format_filename(prj.repoDir))
    ctx.obj = prj


@project_cli.command()
@click.pass_context
def keys(ctx):
    prj = ctx.obj
    click.echo(list(prj.keys()))


@project_cli.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    prj = ctx.obj
    click.echo('[%s]=%s' % (key, prj.get(key)))


@project_cli.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key, value):
    prj = ctx.obj
    prj.set(key, value)


@project_cli.command()
@click.pass_context
def rebuild(ctx):
    prj = ctx.obj
    click.echo("rebuilding")
    prj.rebuild()


@project_cli.command()
@click.argument('name')
@click.option(
    '--filetype',
    default='python',
    type=click.Choice(list(TEMPLATE_CHOICES_DICT.keys())))
@click.pass_context
def create(ctx, name, filetype):
    prj = ctx.obj
    f = prj.create_file(filetype, name)
    click.echo('%s created' % (f.path))


@project_cli.command()
@click.pass_context
def update_pyproj(ctx):
    prj = ctx.obj
    try:
        prj.update_pyproj()
    except Exception as er:
        click.echo(er)
    click.echo('%s updated' % (prj.pyproj))


@project_cli.command()
@click.argument('name')
@click.pass_context
def toxenv(ctx, name):
    prj = ctx.obj
    toxenv = prj.toxEnv
    if name not in list(toxenv.pythonEnvs.keys()):
        raise Exception(
            _('no environment named %s. %s' %
              (name, list(toxenv.pythonEnvs.keys()))))
    toxenv.pythonEnvs.get('name').activate()


@click.group()
@click.pass_context
def toxenv_cli(ctx):
    prj = Project()
    toxenv = prj.toxEnv
    click.echo('Tox from project %s (%s)' % (prj.projectName, prj.repoDir))
    ctx.obj = toxenv


@toxenv_cli.command()
@click.argument('name')
@click.pass_context
def activate(ctx, name):
    toxenv = ctx.obj
    if name not in list(toxenv.pythonEnvs.keys()):
        raise Exception(
            _('no environment named %s. %s' %
              (name, list(toxenv.pythonEnvs.keys()))))
    toxenv.pythonEnvs.get('name').activate()


@toxenv_cli.command()
@click.pass_context
def list_envs(ctx):
    toxenv = ctx.obj
    for e in list(toxenv.pythonEnvs.keys()):
        click.echo(e, e.version, e.archi)
